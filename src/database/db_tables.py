from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(unique=True)
    rights: Mapped[int] = mapped_column(CheckConstraint("rights BETWEEN 1 and 4"))
    is_banned: Mapped[bool]

    user_places: Mapped[list["UserPlace"]] = relationship(
        back_populates="parent_user", cascade="all, delete-orphan"
    )

    user_channels: Mapped[list["TelegramChannel"]] = relationship(
        back_populates="parent_user", cascade="all, delete-orphan"
    )

    user_add_place_requests: Mapped[list["AddPlaceRequest"]] = relationship(
        back_populates="parent_user", cascade="all, delete-orphan"
    )


class Place(Base):
    __tablename__ = "place"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    address: Mapped[str] = mapped_column(unique=True)
    desc: Mapped[str | None]

    user_places: Mapped[list["UserPlace"]] = relationship(
        back_populates="parent_place", cascade="all, delete-orphan"
    )
    place_tags: Mapped[list["Tag"]] = relationship(
        back_populates="parent_place", cascade="all, delete-orphan"
    )


class UserPlace(Base):
    __tablename__ = "user_place"

    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address))
    score: Mapped[int | None] = mapped_column(CheckConstraint("score BETWEEN 1 and 10"))
    comment: Mapped[str | None]

    parent_user: Mapped["User"] = relationship(back_populates="user_places")
    parent_place: Mapped["Place"] = relationship(back_populates="user_places")

    UniqueConstraint(fk_user_id, fk_place_address)

    __mapper_args__ = {"primary_key": [fk_user_id, fk_place_address]}


class Tag(Base):
    __tablename__ = "tag"

    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address))
    place_tag: Mapped[str] = mapped_column()

    parent_place: Mapped["Place"] = relationship(back_populates="place_tags")

    UniqueConstraint(fk_place_address, place_tag)

    __mapper_args__ = {"primary_key": [fk_place_address, place_tag]}


class TelegramChannel(Base):
    __tablename__ = "telegram_channel"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_username: Mapped[str] = mapped_column(unique=True)
    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    parent_user: Mapped["User"] = relationship(back_populates="user_channels")


class AddPlaceRequest(Base):
    __tablename__ = "add_place_request"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    place_name: Mapped[str]
    address: Mapped[str]
    description: Mapped[str | None]
    tags_formatted: Mapped[str]
    is_operated: Mapped[bool]

    parent_user: Mapped["User"] = relationship(back_populates="user_add_place_requests")
