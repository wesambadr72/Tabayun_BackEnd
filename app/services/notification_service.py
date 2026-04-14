import resend
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import User, Notification, Category
from app.core.config import settings

# تهيئة Resend
resend.api_key = settings.RESEND_API_KEY

class NotificationService:
    """خدمة الإشعارات (In-app و Email)"""

    @staticmethod
    async def notify_new_law(db: Session, category_id: int, law_title: str):
        """إرسال إشعارات عند إضافة قانون جديد للمشتركين في القسم"""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return

        # 1. جلب المستخدمين المشتركين في هذا القسم (الذين ضغطوا الجرس)
        subscribers = category.subscribers

        for user in subscribers:
            # أ. إشعار داخل التطبيق (In-app)
            new_notif = Notification(
                title=f"⭐ قانون جديد في قسم {category.name}",
                content=f"🚨 تم إضافة قانون جديد بعنوان:  {law_title}",
                category_id=category_id,
                is_broadcast=False,
                target_user_id=user.id
            )
            db.add(new_notif)

            # ب. إشعار عبر البريد الإلكتروني (Resend)
            if user.email:
                try:
                    resend.Emails.send({
                        "from": "Tabayun <notifications@tabayun.com>",
                        "to": user.email,
                        "subject": f"تنبيه: قانون جديد في {category.name}",
                        "html": f"""
                            <h3>مرحباً {user.full_name}،</h3>
                            <p>نود إعلامك بأنه تم إضافة مادة قانونية جديدة في قسم <b>{category.name}</b> الذي تشترك به.</p>
                            <p><b>العنوان:</b> {law_title}</p>
                            <p>يمكنك الاطلاع على التفاصيل الآن عبر موقع تباين.</p>
                            <br/>
                            <p>مع تحيات فريق تباين.</p>
                        """
                    })
                except Exception as e:
                    print(f"Error sending email to {user.email}: {e}")

        db.commit()

    @staticmethod
    async def send_broadcast_notification(db: Session, title: str, content: str):
        """إرسال إشعار عام من الآدمن لجميع المستخدمين (In-app فقط)"""
        notification = Notification(
            title=title,
            content=content,
            is_broadcast=True
        )
        db.add(notification)
        db.commit()