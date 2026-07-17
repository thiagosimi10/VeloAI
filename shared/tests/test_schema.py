"""Testes estruturais dos modelos de schema compartilhados: garantem que as tabelas do
Banco Master e do template de tenant são criáveis e aceitam inserções básicas.

Usa SQLite em memória apenas para validar a definição dos modelos (colunas, defaults,
relacionamentos) — as migrations reais (Alembic, PostgreSQL) vivem no Provisioning."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from veloai_shared.schema.master import (
    MasterBase,
    Plan,
    Tenant,
    TenantStatus,
    TenantUserIndex,
)
from veloai_shared.schema.tenant import (
    AccountPayable,
    AccountReceivable,
    AiAction,
    AiConversation,
    Attachment,
    CashFlowEntry,
    Category,
    Company,
    Customer,
    KnowledgeDocument,
    LoginHistory,
    Product,
    RefreshToken,
    Sale,
    SaleItem,
    Service,
    ServiceOrder,
    ServiceOrderItem,
    StockMovement,
    Supplier,
    TenantBase,
    TenantPermission,
    TenantRole,
    TenantRolePermission,
    TenantUser,
)


@pytest.fixture
def master_session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    MasterBase.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def tenant_session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    TenantBase.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_tenant_and_plan_round_trip(master_session: Session) -> None:
    plan = Plan(name="VeloAI Professional", price=Decimal("129.90"), trial_days=14)
    master_session.add(plan)
    master_session.flush()

    tenant = Tenant(
        legal_name="Empresa Teste LTDA",
        document="12345678000199",
        database_name="tenant_abc123",
        database_host="localhost",
        database_port=5432,
        plan_id=plan.id,
    )
    master_session.add(tenant)
    master_session.commit()

    fetched = master_session.get(Tenant, tenant.id)
    assert fetched is not None
    assert fetched.status == TenantStatus.PROVISIONING.value
    assert fetched.plan_id == plan.id


def test_tenant_user_index_round_trip(master_session: Session) -> None:
    tenant = Tenant(
        legal_name="Empresa Teste LTDA",
        document="98765432000188",
        database_name="tenant_def456",
        database_host="localhost",
        database_port=5432,
    )
    master_session.add(tenant)
    master_session.flush()

    index_entry = TenantUserIndex(email="admin@empresa.test", tenant_id=tenant.id)
    master_session.add(index_entry)
    master_session.commit()

    fetched = master_session.get(TenantUserIndex, index_entry.id)
    assert fetched is not None
    assert fetched.tenant_id == tenant.id


def test_tenant_schema_user_role_permission_round_trip(tenant_session: Session) -> None:
    company = Company(legal_name="Empresa Teste LTDA", document="12345678000199")
    tenant_session.add(company)
    tenant_session.flush()

    role = TenantRole(name="Administrador")
    permission = TenantPermission(module="system", action="admin")
    tenant_session.add_all([role, permission])
    tenant_session.flush()

    tenant_session.add(TenantRolePermission(role_id=role.id, permission_id=permission.id))

    user = TenantUser(
        company_id=company.id,
        role_id=role.id,
        first_name="Maria",
        email="maria@empresa.test",
        password_hash="hashed",
    )
    tenant_session.add(user)
    tenant_session.commit()

    fetched = tenant_session.get(TenantUser, user.id)
    assert fetched is not None
    assert fetched.force_password_change is True
    assert fetched.active is True


def test_refresh_token_and_login_history_round_trip(tenant_session: Session) -> None:
    company = Company(legal_name="Empresa Teste LTDA", document="12345678000199")
    role = TenantRole(name="Administrador")
    tenant_session.add_all([company, role])
    tenant_session.flush()

    user = TenantUser(
        company_id=company.id,
        role_id=role.id,
        first_name="Maria",
        email="maria@empresa.test",
        password_hash="hashed",
    )
    tenant_session.add(user)
    tenant_session.flush()

    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash="a" * 64,
        expires_at=datetime.now(UTC) + timedelta(days=14),
    )
    login_entry = LoginHistory(user_id=user.id, email=user.email, success=True)
    tenant_session.add_all([refresh_token, login_entry])
    tenant_session.commit()

    assert tenant_session.get(RefreshToken, refresh_token.id) is not None
    fetched_login = tenant_session.get(LoginHistory, login_entry.id)
    assert fetched_login is not None
    assert fetched_login.success is True


def test_customer_round_trip(tenant_session: Session) -> None:
    customer = Customer(
        code="C000001",
        type="PF",
        name="João Silva",
        document="12345678901",
        email="joao@empresa.test",
    )
    tenant_session.add(customer)
    tenant_session.commit()

    fetched = tenant_session.get(Customer, customer.id)
    assert fetched is not None
    assert fetched.active is True
    assert fetched.country == "Brasil"


def test_customer_type_check_constraint_rejects_invalid_value(tenant_session: Session) -> None:
    customer = Customer(code="C000002", type="XX", name="Inválido", document="98765432100")
    tenant_session.add(customer)

    with pytest.raises(IntegrityError):
        tenant_session.commit()


def test_supplier_round_trip(tenant_session: Session) -> None:
    supplier = Supplier(
        code="F000001",
        type="PJ",
        name="Tech Distribuidora LTDA",
        document="12345678000199",
        email="contato@techdistribuidora.test",
    )
    tenant_session.add(supplier)
    tenant_session.commit()

    fetched = tenant_session.get(Supplier, supplier.id)
    assert fetched is not None
    assert fetched.active is True
    assert fetched.country == "Brasil"


def test_supplier_type_check_constraint_rejects_invalid_value(tenant_session: Session) -> None:
    supplier = Supplier(code="F000002", type="XX", name="Inválido", document="98765432100")
    tenant_session.add(supplier)

    with pytest.raises(IntegrityError):
        tenant_session.commit()


def test_category_round_trip(tenant_session: Session) -> None:
    category = Category(name="Armazenamento", description="SSDs, HDs e pendrives")
    tenant_session.add(category)
    tenant_session.commit()

    fetched = tenant_session.get(Category, category.id)
    assert fetched is not None
    assert fetched.name == "Armazenamento"


def test_product_round_trip_with_category_and_supplier(tenant_session: Session) -> None:
    category = Category(name="Armazenamento")
    supplier = Supplier(code="F000001", type="PJ", name="Tech LTDA", document="12345678000199")
    tenant_session.add_all([category, supplier])
    tenant_session.flush()

    product = Product(
        category_id=category.id,
        supplier_id=supplier.id,
        sku="SSD-KGN-1TB",
        name="SSD Kingston 1TB",
        cost_price=Decimal("320.00"),
        sale_price=Decimal("490.00"),
        stock=20,
    )
    tenant_session.add(product)
    tenant_session.commit()

    fetched = tenant_session.get(Product, product.id)
    assert fetched is not None
    assert fetched.unit == "UN"
    assert fetched.active is True
    assert fetched.category_id == category.id
    assert fetched.supplier_id == supplier.id


def test_product_round_trip_without_category_or_supplier(tenant_session: Session) -> None:
    product = Product(
        sku="AVULSO-001",
        name="Produto Avulso",
        cost_price=Decimal("10.00"),
        sale_price=Decimal("15.00"),
    )
    tenant_session.add(product)
    tenant_session.commit()

    fetched = tenant_session.get(Product, product.id)
    assert fetched is not None
    assert fetched.category_id is None
    assert fetched.supplier_id is None


def test_product_stock_check_constraint_rejects_negative_value(tenant_session: Session) -> None:
    product = Product(
        sku="NEGATIVO-001",
        name="Produto Inválido",
        cost_price=Decimal("10.00"),
        sale_price=Decimal("15.00"),
        stock=-1,
    )
    tenant_session.add(product)

    with pytest.raises(IntegrityError):
        tenant_session.commit()


def test_service_round_trip_with_category(tenant_session: Session) -> None:
    category = Category(name="Manutenção")
    tenant_session.add(category)
    tenant_session.flush()

    service = Service(
        category_id=category.id,
        code="S000001",
        name="Formatação de Computador",
        price=Decimal("180.00"),
        estimated_time=60,
    )
    tenant_session.add(service)
    tenant_session.commit()

    fetched = tenant_session.get(Service, service.id)
    assert fetched is not None
    assert fetched.active is True
    assert fetched.category_id == category.id
    assert fetched.estimated_time == 60


def test_service_round_trip_without_category(tenant_session: Session) -> None:
    service = Service(code="S000002", name="Diagnóstico", price=Decimal("50.00"))
    tenant_session.add(service)
    tenant_session.commit()

    fetched = tenant_session.get(Service, service.id)
    assert fetched is not None
    assert fetched.category_id is None
    assert fetched.estimated_time is None


def test_stock_movement_round_trip(tenant_session: Session) -> None:
    product = Product(
        sku="SSD-KGN-1TB",
        name="SSD Kingston 1TB",
        cost_price=Decimal("320.00"),
        sale_price=Decimal("490.00"),
        stock=20,
    )
    tenant_session.add(product)
    tenant_session.flush()

    movement = StockMovement(
        product_id=product.id,
        movement="in",
        quantity=10,
        previous_stock=20,
        current_stock=30,
        reason="Compra de reposição",
    )
    tenant_session.add(movement)
    tenant_session.commit()

    fetched = tenant_session.get(StockMovement, movement.id)
    assert fetched is not None
    assert fetched.product_id == product.id
    assert fetched.current_stock == 30


def test_service_order_round_trip_with_technician(tenant_session: Session) -> None:
    company = Company(legal_name="Empresa Teste LTDA", document="12345678000199")
    role = TenantRole(name="Técnico")
    tenant_session.add_all([company, role])
    tenant_session.flush()

    technician = TenantUser(
        company_id=company.id,
        role_id=role.id,
        first_name="Carlos",
        email="carlos@empresa.test",
        password_hash="hashed",
    )
    customer = Customer(code="C000001", type="PF", name="João Silva", document="12345678901")
    tenant_session.add_all([technician, customer])
    tenant_session.flush()

    order = ServiceOrder(
        number="OS-2026-000001",
        customer_id=customer.id,
        technician_id=technician.id,
        equipment="Notebook Dell Latitude",
        problem="Não liga",
    )
    tenant_session.add(order)
    tenant_session.commit()

    fetched = tenant_session.get(ServiceOrder, order.id)
    assert fetched is not None
    assert fetched.status == "open"
    assert fetched.total == Decimal("0.00")
    assert fetched.technician_id == technician.id


def test_service_order_round_trip_without_technician(tenant_session: Session) -> None:
    customer = Customer(code="C000002", type="PF", name="Maria Souza", document="98765432100")
    tenant_session.add(customer)
    tenant_session.flush()

    order = ServiceOrder(number="OS-2026-000002", customer_id=customer.id)
    tenant_session.add(order)
    tenant_session.commit()

    fetched = tenant_session.get(ServiceOrder, order.id)
    assert fetched is not None
    assert fetched.technician_id is None
    assert fetched.finished_at is None


def test_service_order_item_round_trip_with_product_and_service(
    tenant_session: Session,
) -> None:
    customer = Customer(code="C000003", type="PF", name="Ana Lima", document="11144477735")
    product = Product(
        sku="SSD-KGN-1TB",
        name="SSD Kingston 1TB",
        cost_price=Decimal("320.00"),
        sale_price=Decimal("490.00"),
    )
    service = Service(code="S000001", name="Formatação", price=Decimal("180.00"))
    tenant_session.add_all([customer, product, service])
    tenant_session.flush()

    order = ServiceOrder(number="OS-2026-000003", customer_id=customer.id)
    tenant_session.add(order)
    tenant_session.flush()

    product_item = ServiceOrderItem(
        service_order_id=order.id,
        product_id=product.id,
        quantity=1,
        unit_price=Decimal("490.00"),
        total=Decimal("490.00"),
    )
    service_item = ServiceOrderItem(
        service_order_id=order.id,
        service_id=service.id,
        quantity=1,
        unit_price=Decimal("180.00"),
        total=Decimal("180.00"),
    )
    tenant_session.add_all([product_item, service_item])
    tenant_session.commit()

    fetched_product_item = tenant_session.get(ServiceOrderItem, product_item.id)
    fetched_service_item = tenant_session.get(ServiceOrderItem, service_item.id)
    assert fetched_product_item is not None
    assert fetched_product_item.product_id == product.id
    assert fetched_product_item.service_id is None
    assert fetched_service_item is not None
    assert fetched_service_item.service_id == service.id
    assert fetched_service_item.product_id is None


def test_sale_round_trip(tenant_session: Session) -> None:
    customer = Customer(code="C000004", type="PF", name="Pedro Alves", document="52998224725")
    tenant_session.add(customer)
    tenant_session.flush()

    sale = Sale(customer_id=customer.id, payment_method="pix")
    tenant_session.add(sale)
    tenant_session.commit()

    fetched = tenant_session.get(Sale, sale.id)
    assert fetched is not None
    assert fetched.status == "open"
    assert fetched.total == Decimal("0.00")
    assert fetched.discount == Decimal("0.00")
    assert fetched.payment_method == "pix"


def test_sale_item_round_trip(tenant_session: Session) -> None:
    customer = Customer(code="C000005", type="PF", name="Lucas Rocha", document="15350946056")
    product = Product(
        sku="SSD-KGN-1TB",
        name="SSD Kingston 1TB",
        cost_price=Decimal("320.00"),
        sale_price=Decimal("490.00"),
    )
    tenant_session.add_all([customer, product])
    tenant_session.flush()

    sale = Sale(customer_id=customer.id)
    tenant_session.add(sale)
    tenant_session.flush()

    item = SaleItem(
        sale_id=sale.id, product_id=product.id, quantity=2, unit_price=Decimal("490.00")
    )
    tenant_session.add(item)
    tenant_session.commit()

    fetched = tenant_session.get(SaleItem, item.id)
    assert fetched is not None
    assert fetched.sale_id == sale.id
    assert fetched.product_id == product.id
    assert fetched.quantity == 2


def test_account_receivable_round_trip(tenant_session: Session) -> None:
    customer = Customer(code="C000006", type="PF", name="Beatriz Nunes", document="16899027036")
    tenant_session.add(customer)
    tenant_session.flush()

    receivable = AccountReceivable(
        customer_id=customer.id, due_date=date(2026, 8, 1), amount=Decimal("980.00")
    )
    tenant_session.add(receivable)
    tenant_session.commit()

    fetched = tenant_session.get(AccountReceivable, receivable.id)
    assert fetched is not None
    assert fetched.status == "pending"
    assert fetched.payment_date is None
    assert fetched.amount == Decimal("980.00")


def test_account_payable_round_trip(tenant_session: Session) -> None:
    supplier = Supplier(code="F000002", type="PJ", name="Tech LTDA", document="12345678000199")
    tenant_session.add(supplier)
    tenant_session.flush()

    payable = AccountPayable(
        supplier_id=supplier.id, due_date=date(2026, 8, 10), amount=Decimal("320.00")
    )
    tenant_session.add(payable)
    tenant_session.commit()

    fetched = tenant_session.get(AccountPayable, payable.id)
    assert fetched is not None
    assert fetched.status == "pending"
    assert fetched.payment_date is None
    assert fetched.amount == Decimal("320.00")


def test_cash_flow_entry_round_trip(tenant_session: Session) -> None:
    entry = CashFlowEntry(
        type="in", category="Recebimento", description="Teste", amount=Decimal("980.00")
    )
    tenant_session.add(entry)
    tenant_session.commit()

    fetched = tenant_session.get(CashFlowEntry, entry.id)
    assert fetched is not None
    assert fetched.type == "in"
    assert fetched.date is not None


def test_attachment_round_trip(tenant_session: Session) -> None:
    company = Company(legal_name="Empresa Teste LTDA", document="12345678000199")
    role = TenantRole(name="Administrador")
    tenant_session.add_all([company, role])
    tenant_session.flush()

    user = TenantUser(
        company_id=company.id,
        role_id=role.id,
        first_name="Maria",
        email="maria@empresa.test",
        password_hash="hashed",
    )
    tenant_session.add(user)
    tenant_session.flush()

    resource_id = uuid.uuid4()
    attachment = Attachment(
        resource_type="service_order",
        resource_id=resource_id,
        original_filename="foto.jpg",
        storage_key=f"tenant-abc/service_order/{resource_id}/foto.jpg",
        content_type="image/jpeg",
        size_bytes=1024,
        uploaded_by=user.id,
    )
    tenant_session.add(attachment)
    tenant_session.commit()

    fetched = tenant_session.get(Attachment, attachment.id)
    assert fetched is not None
    assert fetched.resource_type == "service_order"
    assert fetched.resource_id == resource_id
    assert fetched.uploaded_by == user.id
    assert fetched.created_at is not None


def test_ai_conversation_round_trip(tenant_session: Session) -> None:
    company = Company(legal_name="Empresa Teste LTDA", document="12345678000199")
    role = TenantRole(name="Administrador")
    tenant_session.add_all([company, role])
    tenant_session.flush()

    user = TenantUser(
        company_id=company.id,
        role_id=role.id,
        first_name="Maria",
        email="maria2@empresa.test",
        password_hash="hashed",
    )
    tenant_session.add(user)
    tenant_session.flush()

    conversation = AiConversation(
        user_id=user.id,
        prompt="Quanto vendi em maio?",
        response="Você vendeu R$ 12.340,00 em maio.",
        tokens=128,
        model="gemini-3.1-flash-lite",
        execution_time=Decimal("1.234"),
    )
    tenant_session.add(conversation)
    tenant_session.commit()

    fetched = tenant_session.get(AiConversation, conversation.id)
    assert fetched is not None
    assert fetched.user_id == user.id
    assert fetched.tokens == 128
    assert fetched.model == "gemini-3.1-flash-lite"
    assert fetched.created_at is not None


def test_ai_action_round_trip(tenant_session: Session) -> None:
    company = Company(legal_name="Empresa Teste LTDA", document="12345678000199")
    role = TenantRole(name="Administrador")
    tenant_session.add_all([company, role])
    tenant_session.flush()

    user = TenantUser(
        company_id=company.id,
        role_id=role.id,
        first_name="Maria",
        email="maria3@empresa.test",
        password_hash="hashed",
    )
    tenant_session.add(user)
    tenant_session.flush()

    conversation = AiConversation(
        user_id=user.id,
        prompt="Cadastre um cliente chamado João Silva.",
        response="Cliente João Silva cadastrado com sucesso.",
        tokens=96,
        model="gemini-3.1-flash-lite",
        execution_time=Decimal("2.150"),
    )
    tenant_session.add(conversation)
    tenant_session.flush()

    action = AiAction(
        conversation_id=conversation.id,
        tool="CreateCustomer",
        service="customers",
        execution={"arguments": {"name": "João Silva"}, "result": {"id": "some-uuid"}},
        success=True,
    )
    tenant_session.add(action)
    tenant_session.commit()

    fetched = tenant_session.get(AiAction, action.id)
    assert fetched is not None
    assert fetched.conversation_id == conversation.id
    assert fetched.tool == "CreateCustomer"
    assert fetched.service == "customers"
    assert fetched.success is True
    assert fetched.execution == {
        "arguments": {"name": "João Silva"},
        "result": {"id": "some-uuid"},
    }
    assert fetched.created_at is not None


def test_knowledge_document_round_trip(tenant_session: Session) -> None:
    company = Company(legal_name="Empresa Teste LTDA", document="12345678000199")
    role = TenantRole(name="Administrador")
    tenant_session.add_all([company, role])
    tenant_session.flush()

    user = TenantUser(
        company_id=company.id,
        role_id=role.id,
        first_name="Maria",
        email="maria4@empresa.test",
        password_hash="hashed",
    )
    tenant_session.add(user)
    tenant_session.flush()

    document = KnowledgeDocument(
        title="Política de Garantia",
        content="Todo produto tem garantia de 90 dias contra defeitos de fabricação.",
        created_by=user.id,
    )
    tenant_session.add(document)
    tenant_session.commit()

    fetched = tenant_session.get(KnowledgeDocument, document.id)
    assert fetched is not None
    assert fetched.title == "Política de Garantia"
    assert fetched.created_by == user.id
    assert fetched.created_at is not None
    assert fetched.updated_at is not None
    assert fetched.deleted_at is None
