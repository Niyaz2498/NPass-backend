from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Base = declarative_base()

class Users(db.Model):
    __tablename__ = "users"

    # id: Mapped[int] = mapped_column(String(30), primary_key=True)
    # username: Mapped[str] = mapped_column(String(0), unique=True, nullable=False)

    email: Mapped[str] = mapped_column(String(30), primary_key=True, nullable=False)
    UserName: Mapped[str] = mapped_column(String(30), nullable=False)
    UserID: Mapped[str] = mapped_column(String(30), nullable=False)
    HashedMessage: Mapped[str] = mapped_column(String(30), nullable=False)

    def __repr__(self) -> str:
        return "\nid: {id} \nusername: {uname} \nmail: {email}\nhashedmsg:{msg}\n".format(id = self.UserID, uname = self.UserName, email = self.email, msg = self.HashedMessage)

