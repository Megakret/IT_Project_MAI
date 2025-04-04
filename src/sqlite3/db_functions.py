from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)


class Place(Base):
    __tablename__ = "place"

    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(unique=True, nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)
    rate: Mapped[int] = mapped_column(CheckConstraint("rate BETWEEN 1 and 10"), nullable=False)

    __mapper_args__ = {
        "primary_key": address
    }


class CustomPlace(Base):
    __tablename__ = "custom_place"

    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)
    rate: Mapped[int] = mapped_column(CheckConstraint("rate BETWEEN 1 and 10"), nullable=False)
    fk_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    UniqueConstraint(address, fk_user_id)

    __mapper_args__ = {
        "primary_key": (address, fk_user_id)
    }


def AddCustomPlace(name: str, address: str, rate: int, desc: str | None, user_id: int) -> None:
    engine = create_engine("sqlite:///db.db")
    with Session(engine) as session:
        try:
            session.add(
                CustomPlace(
                    name=name,
                    address=address,
                    desc=desc,
                    rate=rate,
                    fk_user_id=user_id,
                )
            )
            session.flush()
        except IntegrityError:
            session.rollback()
            raise
        else:
            session.commit()


engine = create_engine("sqlite:///db.db")
Base.metadata.create_all(engine)
