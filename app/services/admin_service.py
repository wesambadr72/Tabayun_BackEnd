from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Optional, Dict, Any
from app.db.models import (
    User, LegalContent, ComparativeLaw, AuditLog, 
    SystemConfig, Notification, Category
)
from app.schemas.admin import AdminDashboardStats
from app.services.notification_service import NotificationService

class AdminService:
    @staticmethod
    def get_dashboard_stats(db: Session) -> AdminDashboardStats:
        """
        إرجاع إحصائيات لوحة التحكم
        """
        total_laws = db.query(func.count(LegalContent.id)).scalar() or 0
        total_countries = db.query(func.count(distinct(LegalContent.country))).scalar() or 0
        total_comparisons = db.query(func.count(ComparativeLaw.id)).scalar() or 0
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_categories = db.query(func.count(Category.id)).scalar() or 0
        
        return AdminDashboardStats(
            total_laws=total_laws,
            total_countries=total_countries,
            total_comparisons=total_comparisons,
            total_users=total_users,
            total_categories=total_categories
        )

    #  إدارة القوانين (Law Management)

    @staticmethod
    async def add_law(db: Session, admin_id: int, law_data: Dict[str, Any]) -> LegalContent:
        """إضافة قانون جديد وإشعار المشتركين"""
        # Mapping frontend fields to backend fields
        mapped_data = {
            "title": law_data.get("title"),
            "country": law_data.get("country"),
            "category_id": law_data.get("category_id"),
            "original_text": law_data.get("text") or law_data.get("original_text") or "",
            "simplified_text": law_data.get("simplified_text") or "",
            "article_number": law_data.get("article_number"),
            "source_url": law_data.get("source_url"),
            "aria_label": law_data.get("simplified_description") or law_data.get("aria_label"),
            "alt_text": law_data.get("keywords") or law_data.get("alt_text"),
            "importance_score": 0,
            "is_live": 1
        }
        
        # Remove None values to let DB defaults work
        final_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        try:
            # التحقق مما إذا كان العنوان موجوداً مسبقاً لتجنب التكرار في حال إعادة المحاولة
            existing = db.query(LegalContent).filter(
                LegalContent.title == final_data["title"],
                LegalContent.country == final_data["country"]
            ).first()
            
            if existing:
                new_law = existing
            else:
                new_law = LegalContent(**final_data)
                db.add(new_law)
                db.commit()
                db.refresh(new_law)
            
            # إذا كان قانوناً أجنبياً وله مرجع سعودي، قم بإنشاء مقارنة تلقائياً
            saudi_ref_id = law_data.get("saudi_reference_id")
            if saudi_ref_id and final_data.get("country", "").lower() != "sa":
                # التأكد من وجود القانون السعودي
                saudi_law = db.query(LegalContent).filter(LegalContent.id == saudi_ref_id).first()
                if saudi_law:
                    # التأكد من عدم وجود مقارنة مسبقة
                    existing_comp = db.query(ComparativeLaw).filter(
                        ComparativeLaw.saudi_law_id == saudi_ref_id,
                        ComparativeLaw.foreign_law_id == new_law.id
                    ).first()
                    
                    if not existing_comp:
                        comparison = ComparativeLaw(
                            saudi_law_id=saudi_ref_id,
                            foreign_law_id=new_law.id,
                            summary=new_law.simplified_text[:200]
                        )
                        db.add(comparison)
                        db.commit()

            # تسجيل العملية
            AdminService.log_action(
                db, admin_id, "ADD_LAW", "legal_contents", 
                new_law.id, None, final_data
            )

            # استدعاء منطق الإشعارات (منفصل)
            try:
                await AdminService._trigger_law_notifications(db, new_law)
            except Exception as e:
                print(f"Notification error: {e}")
            
            return new_law
        except Exception as e:
            db.rollback()
            print(f"Error in add_law: {str(e)}") # للتشخيص
            raise e

    @staticmethod
    async def _trigger_law_notifications(db: Session, law: LegalContent):
        """منطق إرسال الإشعارات المنفصل عند إضافة قانون جديد"""
        await NotificationService.notify_new_law(
            db, law.category_id, law.title
        )

    @staticmethod
    def update_law(db: Session, admin_id: int, law_id: int, update_data: Dict[str, Any]) -> Optional[LegalContent]:
        """تعديل قانون موجود وتحديث المقارنة إذا لزم الأمر"""
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law:
            return None
        
        # استخراج المرجع السعودي قبل الحذف من البيانات المرسلة للقاعدة
        saudi_ref_id = update_data.get("saudi_reference_id")
        
        # تنظيف البيانات (Mapping)
        mapped_data = {
            "title": update_data.get("title"),
            "country": update_data.get("country"),
            "category_id": update_data.get("category_id"),
            "original_text": update_data.get("text") or update_data.get("original_text"),
            "simplified_text": update_data.get("simplified_text"),
            "article_number": update_data.get("article_number"),
            "source_url": update_data.get("source_url"),
            "aria_label": update_data.get("simplified_description") or update_data.get("aria_label"),
            "alt_text": update_data.get("keywords") or update_data.get("alt_text")
        }
        
        # تحديث الحقول الموجودة فقط
        final_update = {k: v for k, v in mapped_data.items() if v is not None}
        
        old_values = {column.name: getattr(law, column.name) for column in law.__table__.columns if column.name in final_update}
        
        for key, value in final_update.items():
            setattr(law, key, value)
        
        db.commit()
        db.refresh(law)

        # تحديث أو إنشاء المقارنة تلقائياً
        if saudi_ref_id and law.country.lower() != "sa":
            # التحقق مما إذا كانت هناك مقارنة موجودة
            existing_comp = db.query(ComparativeLaw).filter(ComparativeLaw.foreign_law_id == law.id).first()
            if existing_comp:
                existing_comp.saudi_law_id = saudi_ref_id
                existing_comp.summary = law.simplified_text[:200]
            else:
                new_comp = ComparativeLaw(
                    saudi_law_id=saudi_ref_id,
                    foreign_law_id=law.id,
                    summary=law.simplified_text[:200]
                )
                db.add(new_comp)
            db.commit()
        
        # تسجيل العملية
        AdminService.log_action(
            db, admin_id, "UPDATE_LAW", "legal_contents", 
            law.id, old_values, final_update
        )
        return law

    @staticmethod
    def delete_law(db: Session, admin_id: int, law_id: int) -> bool:
        """حذف قانون"""
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law:
            return False
        
        old_values = {column.name: getattr(law, column.name) for column in law.__table__.columns}
        db.delete(law)
        db.commit()
        
        # تسجيل العملية
        AdminService.log_action(
            db, admin_id, "DELETE_LAW", "legal_contents", 
            law_id, old_values, None
        )
        return True

    @staticmethod
    def bulk_delete_laws(db: Session, admin_id: int, law_ids: List[int]) -> int:
        """حذف مجموعة من القوانين دفعة واحدة"""
        laws = db.query(LegalContent).filter(LegalContent.id.in_(law_ids)).all()
        deleted_count = 0
        for law in laws:
            old_values = {column.name: getattr(law, column.name) for column in law.__table__.columns}
            db.delete(law)
            AdminService.log_action(
                db, admin_id, "DELETE_LAW", "legal_contents", 
                law.id, old_values, None
            )
            deleted_count += 1
        db.commit()
        return deleted_count

    # --- جلب البيانات للقوائم (Listing Methods) ---

    @staticmethod
    def get_law_by_id(db: Session, law_id: int) -> Optional[LegalContent]:
        """جلب تفاصيل قانون واحد باستخدام ID"""
        return db.query(LegalContent).filter(LegalContent.id == law_id).first()

    @staticmethod
    def get_all_laws(db: Session, skip: int = 0, limit: int = 100, search: str = None, category_id: Optional[int] = None) -> List[LegalContent]:
        """جلب قائمة القوانين للآدمن مع البحث والفلترة حسب القسم"""
        query = db.query(LegalContent)
        if category_id:
            query = query.filter(LegalContent.category_id == category_id)
        if search:
            query = query.filter(
                (LegalContent.title.ilike(f"%{search}%")) | 
                (LegalContent.country.ilike(f"%{search}%"))
            )
        return query.order_by(LegalContent.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100, search: str = None) -> List[User]:
        """جلب قائمة المستخدمين للآدمن مع البحث"""
        query = db.query(User)
        if search:
            query = query.filter(
                (User.full_name.ilike(f"%{search}%")) | 
                (User.email.ilike(f"%{search}%"))
            )
        return query.order_by(User.id.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_configs(db: Session) -> List[SystemConfig]:
        """جلب كافة إعدادات النظام"""
        return db.query(SystemConfig).all()

    #  إدارة المستخدمين (User Management)

    @staticmethod
    def delete_user(db: Session, admin_id: int, user_id: int) -> bool:
        """حذف مستخدم"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        old_values = {"email": user.email, "full_name": user.full_name, "role": user.role}
        db.delete(user)
        db.commit()
        
        # تسجيل العملية
        AdminService.log_action(
            db, admin_id, "DELETE_USER", "users", 
            user_id, old_values, None
        )
        return True

    @staticmethod
    def bulk_delete_users(db: Session, admin_id: int, user_ids: List[int]) -> int:
        """حذف مجموعة من المستخدمين دفعة واحدة"""
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        deleted_count = 0
        for user in users:
            old_values = {"email": user.email, "full_name": user.full_name, "role": user.role}
            db.delete(user)
            AdminService.log_action(
                db, admin_id, "DELETE_USER", "users", 
                user.id, old_values, None
            )
            deleted_count += 1
        db.commit()
        return deleted_count

    @staticmethod
    def update_user_role(db: Session, admin_id: int, user_id: int, new_role: str) -> Optional[User]:
        """تعديل صلاحية مستخدم"""
        allowed_roles = ["user", "admin"]
        if new_role not in allowed_roles:
            raise ValueError(f"Role '{new_role}' is not allowed. Choose from {allowed_roles}")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        old_role = user.role
        user.role = new_role
        # تحديث خاصية is_admin بناءً على الدور الجديد
        user.is_admin = (new_role == "admin")
        db.commit()
        db.refresh(user)
        
        # تسجيل العملية
        AdminService.log_action(
            db, admin_id, "UPDATE_USER_ROLE", "users", 
            user_id, {"role": old_role}, {"role": new_role}
        )
        return user

    #  إدارة إعدادات النظام (System Config)

    @staticmethod
    def get_system_config(db: Session, key: str) -> Optional[str]:
        """جلب إعداد من النظام """
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return config.value if config else None

    @staticmethod
    def update_system_config(db: Session, admin_id: int, key: str, value: str, example_value: str = None, description: str = None) -> SystemConfig:
        """تعديل معلومات الذكاء الاصطناعي أو إعدادات النظام"""
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        old_value = config.value if config else "NEW_CONFIG"
        
        if config:
            config.value = value
            if example_value: config.example_value = example_value
            if description: config.description = description
        else:
            config = SystemConfig(key=key, value=value, example_value=example_value, description=description)
            db.add(config)
        
        db.commit()
        db.refresh(config)
        
        # توثيق العملية (Audit Log)
        AdminService.log_action(
            db, admin_id, "UPDATE_SYSTEM_CONFIG", "system_configs", 
            config.id, {"value": old_value}, {"value": value}
        )
        return config

    @staticmethod
    def seed_default_configs(db: Session, admin_id: int):
        """إدخال الإعدادات الافتراضية للنظام حالياً"""
        default_configs = [
            {
                "key": "gemini_model_name",
                "value": "gemini-3.1-flash-lite-preview",
                "example_value": "gemini-3.1-flash-preview",
                "description": "اسم موديل الذكاء الاصطناعي المستخدم في المعالجة"
            },
            {
                "key": "simplification_prompt",
                "value": """Simplify this legal article for a regular person.
            Provide the output in {target_lang}.

            Article Details:
            - Title: {title}
            - Category: {category}
            - Original Text: {law_text}

            Requirements:
            1. Summary: One or two simple and clear sentences summarizing the core rule.
            2. Punishment: Clear explanation of penalties if mentioned, otherwise write 'لا يوجد عقوبات'.

        Constraints:
        - Use friendly, everyday language.
        - Focus on what the person MUST or MUST NOT do.
        - Be extremely concise.
        - Do not change the core meaning of the rule.
        - Do not include any additional information.
        - Do not include any explanations or notes.
        - Respond strictly in JSON format.""",
                "example_value": "قم بتبسيط النص القانوني التالي باللغة العربية بأسلوب سهل وواضح يركز على المحظورات والعقوبات.",
                "description": "البرومبت الخاص بتبسيط القوانين"
            },
            {
                "key": "comparison_prompt",
                "value": """Compare these two legal articles and provide a brief summary of the differences for a tourist.
            The output must be in {target_lang}.

            Saudi Law:
            - Title: {saudi_title}
            - Text: {saudi_text}

            Foreign Law ({foreign_country}):
            - Title: {foreign_title}
            - Text: {foreign_text}

            Requirements:
            1. Comparison Summary: ONE punchy and clear sentence in {target_lang} comparing both (e.g. 'Both require X, but UK has Y').
            2. Saudi Point: Key rule in Saudi Arabia in one short sentence.
            3. Foreign Point: Key rule in the other country in one short sentence.
            4. Conclusion: One short practical advice for the traveler in {target_lang}.

        Constraints:
        - Focus on the most important difference for a tourist.
        - Keep it very brief and direct.
        - Do not include any additional information.
        - Do not include any explanations or notes.
        - Respond strictly in JSON format.""",
                "example_value": "قارن بين القانون السعودي والقانون الأجنبي المذكورين، ووضح أهم فرق جوهري يهم السائح بلغة بسيطة.",
                "description": "البرومبت الخاص بالمقارنة بين قانونين"
            },
            {
                "key": "rank_prompt",
                "value": """Analyze the importance of this legal article for a typical tourist or resident in the country.
                Provide a score from 1 to 10 and a brief reason in English.

                Article Details:
                - Title: {law_title}
                - Category: {category}
                - Text: {law_text}

                Scoring Criteria:
                - 9-10 (Critical): Rules governing direct public behavior, safety, or laws with severe penalties like high fines, detention, or deportation.
                - 7-8 (High): Common daily rules that most tourists will encounter.
                - 5-6 (Medium): Important procedures or documentation that affect the overall journey.
                - 1-4 (Low): Technical definitions or internal government procedures.

                Respond strictly in JSON format.""",
                "example_value": "قيم أهمية هذا القانون للسياح والمقيمين من 1 إلى 10 مع ذكر السبب باختصار باللغة الإنجليزية.",
                "description": "البرومبت الخاص بتقييم أهمية القوانين"
            }
        ]
        
        for cfg in default_configs:
            AdminService.update_system_config(
                db, admin_id, cfg["key"], cfg["value"], 
                cfg["example_value"], cfg["description"]
            )

    #  إدارة الإشعارات (Notifications)

    @staticmethod
    def send_notification(db: Session, admin_id: int, title: str, content: str, target_user_id: int = None) -> Notification:
        """إرسال إشعار لمستخدم أو للجميع"""
        notification = Notification(
            sender_id=admin_id,
            recipient_id=target_user_id,
            title=title,
            message=content,
            is_broadcast=(target_user_id is None),
            target_user_id=target_user_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # تسجيل العملية
        AdminService.log_action(
            db, admin_id, "SEND_NOTIFICATION", "notifications", 
            notification.id, None, {"title": title, "target_user_id": target_user_id}
        )
        return notification

    #  سجلات التعديل (Audit Logs)

    @staticmethod
    def get_audit_logs(db: Session, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """جلب تاريخ التعديلات مع بيانات المستخدم"""
        from sqlalchemy.orm import joinedload
        return db.query(AuditLog).options(joinedload(AuditLog.user)).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    #  دالة مساعدة للتسجيل (Logging Helper)

    @staticmethod
    def log_action(db: Session, user_id: int, action: str, table_name: str, record_id: int = None, old_values: Dict = None, new_values: Dict = None):
        """تسجيل العمليات في AuditLog"""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values
        )
        db.add(log_entry)
        db.commit()
