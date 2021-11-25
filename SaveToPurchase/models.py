import enum
from sqlalchemy import (
    Date,
    Enum,
    Float,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# from . import db


Base = declarative_base()


# Base.query = db.session.query_property()


class MyEnum(str, enum.Enum):
    active = 1
    inactive = 0


class MpesaStatus(str, enum.Enum):
    unprocessed = 0
    processed = 1
    user_not_found = 2


class Payment_Status(str, enum.Enum):
    completed = 1
    incomplete = 0
    inprogress = 2
    inactive = 3


class Language(str, enum.Enum):
    english = 0
    swahili = 1


class AccountEnum(str, enum.Enum):
    spending = 0
    savings = 1


class EntityTypes(Base):
    __tablename__ = "entity_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    active_status = Column(Enum(MyEnum))
    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    end_date = Column(DateTime(timezone=True), default=None)
    live_date = Column(DateTime(timezone=True), default=None)

    entity_associated = relationship('Entity', backref='entity_types')


class Entity(Base):
    __tablename__ = "entity"

    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    entity_type = Column(Integer, ForeignKey('entity_types.id'))
    entity_status = Column(Enum(MyEnum))
    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    entity_users = relationship('Entity_Users', backref='entity')
    entity_kyc = relationship('Entity_Kyc', backref='entity')

    entity_account = relationship('Entity_Account', backref='entity')


class UserTypes(Base):
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True)
    user_type = Column(String(140))
    active_status = Column(Enum(MyEnum))
    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    entity_users = relationship('Entity_Users', backref='user_types')


class Entity_Users(Base):
    __tablename__ = "entity_users"

    id = Column(Integer, primary_key=True)
    user_name = Column(String(140), unique=True)
    password = Column(String(140))
    entity_id = Column(Integer, ForeignKey('entity.id'))
    user_type_id = Column(Integer, ForeignKey('user_types.id'))
    user_status = Column(Enum(MyEnum))
    language = Column(Enum(Language))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    items_selected = relationship('Items_Selected', backref='entity_users')


class Document_Types(Base):
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    description = Column(String(140))
    document_status = Column(Enum(MyEnum))
    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    entity_kyc = relationship('Entity_Kyc', backref='document_types')


class Entity_Kyc(Base):
    __tablename__ = "entity_kyc"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(140), default=None)
    other_names = Column(String(140))
    description = Column(String(140))
    document_id = Column(Integer, ForeignKey('document_types.id'))
    document_number = Column(String(140))

    active_status = Column(Enum(MyEnum))

    entity_owner_id = Column(Integer, ForeignKey('entity.id'))

    country = Column(String(140))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    __table_args__ = (
        UniqueConstraint('document_number', 'country', name='document_number_country'),
    )


class Global_Charts_OF_Accounts(Base):
    __tablename__ = "global_charts_of_account"

    id = Column(Integer, primary_key=True)
    account_type = Column(String(140))
    account_classification = Column(String(140))
    total_amount = Column(Float)
    global_status = Column(Enum(MyEnum))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    __table_args__ = (
        UniqueConstraint('account_type', 'account_classification', name='account_type_account_classification'),
    )

    account_types = relationship('AccountTypes', backref='global_charts_of_account')


class AccountTypes(Base):
    __tablename__ = "account_types"

    id = Column(Integer, primary_key=True)

    account_name = Column(String(140), unique=True)
    account_number = Column(String(140))
    available_amount = Column(Float)
    global_id = Column(Integer, ForeignKey('global_charts_of_account.id'))
    created_by = Column(String(140))
    account_type_status = Column(Enum(MyEnum))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    __table_args__ = (
        UniqueConstraint('account_name', 'account_number', name='account_name_account_number'),
    )
    entity_account = relationship('Entity_Account', backref='account_types')


class Currencies(Base):
    __tablename__ = "currencies_table"

    id = Column(Integer, primary_key=True)

    currency_name = Column(String(140))
    country = Column(String(140))

    currency_status = Column(Enum(MyEnum))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    entity_account = relationship('Entity_Account', backref='currencies_table')


class Entity_Account(Base):
    __tablename__ = "entity_account"

    id = Column(Integer, primary_key=True)
    account_number = Column(String(140))
    description = Column(Enum(AccountEnum))
    available_balance = Column(Float)
    accounts_type_id = Column(Integer, ForeignKey('account_types.id'))
    currency_id = Column(Integer, ForeignKey('currencies_table.id'))
    entity_id = Column(Integer, ForeignKey('entity.id'))
    active_status = Column(Enum(MyEnum))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    items_selected = relationship('Items_Selected', backref='entity_account')


class Services(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    description = Column(String(140))
    service_status = Column(Enum(MyEnum))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)

    transactions = relationship('Transactions', backref='services')
    tariff_charge = relationship('TariffCharges', backref='services')


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    master_transaction_id = Column(String(140))
    transaction_id = Column(String(140))
    account_number = Column(String(140))
    service_id = Column(Integer, ForeignKey('services.id'))

    description = Column(String(140))
    debit = Column(Float)
    credit = Column(Float)
    bal_before = Column(Float)
    bal_after = Column(Float)
    transaction_status = Column(Enum(MyEnum))
    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)


class Items_Inventory(Base):
    __tablename__ = "items_inventory"
    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    model = Column(String(140))
    size = Column(String(140))
    price = Column(Float)

    inventory_status = Column(Enum(MyEnum))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())

    items_selected = relationship('Items_Selected', backref='items_inventory')

    __table_args__ = (
        UniqueConstraint('name', 'model', 'size', name='name_model_size'),
    )


class Items_Selected(Base):
    __tablename__ = "items_selected"

    id = Column(Integer, primary_key=True)
    entity_account_id = Column(Integer, ForeignKey('entity_account.id'))
    entity_user_id = Column(Integer, ForeignKey('entity_users.id'))
    inventory_id = Column(Integer, ForeignKey('items_inventory.id'))
    price = Column(Float)
    savings_made = Column(Float)
    payment_status = Column(Enum(Payment_Status))

    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())

    end_date = Column(DateTime(timezone=True), default=None)


class STK_Results(Base):
    __tablename__ = "stk_results"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(140))
    msisdn = Column(String(140))
    amount = Column(String(140))
    account = Column(String(140))
    item_inventory_id = Column(Integer)
    name = Column(String(140))
    description = Column(String(140))
    reference = Column(String(140))
    status = Column(String(140))
    stk_status = Column(Enum(MpesaStatus))
    created_at = Column(DateTime(timezone=True), default=datetime.now(),
                        onupdate=datetime.now())


class TariffCharges(Base):
    __tablename__ = "tariff_charges"

    id = Column(Integer, primary_key=True)
    min_amount = Column(Float)
    max_amount = Column(Float)
    charges = Column(Float)
    service_id = Column(Integer, ForeignKey('services.id'))
    tariff_status = Column(Enum(MyEnum))
    date_created = Column(DateTime(timezone=True), default=datetime.now(),
                          onupdate=datetime.now())
    live_date = Column(DateTime(timezone=True), default=None)
    end_date = Column(DateTime(timezone=True), default=None)


class USSD_SESSION_LOGS(Base):
    __tablename__ = "ussd_session_logs"
    id = Column(Integer, primary_key=True)

    sessionId = Column(String(140), unique=True)
    serviceCode = Column(String(13))
    msisdn = Column(String(13))
    ussdString = Column(String(5000))
    level = Column(String(5000))
    arguments = Column(String(5000), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.now(),
                        onupdate=datetime.now())
