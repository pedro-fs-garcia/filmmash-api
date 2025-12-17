# 🧪 Guia Completo de Testes

## 📚 Índice

1. [Introdução](#introdução)
2. [Estrutura de Testes](#estrutura-de-testes)
3. [Configuração](#configuração)
4. [Tipos de Testes](#tipos-de-testes)
5. [Fixtures Disponíveis](#fixtures-disponíveis)
6. [Como Escrever Testes](#como-escrever-testes)
7. [Executando Testes](#executando-testes)
8. [Boas Práticas](#boas-práticas)

---

## 📖 Introdução

Este guia te ensina a escrever e executar testes na aplicação Filmmash API.

**Stack de Testes:**
- **pytest**: Framework de testes
- **pytest-asyncio**: Suporte a testes assíncronos
- **httpx**: Cliente HTTP para testes de API
- **SQLAlchemy**: Testes de banco de dados com transações

---

## 🏗️ Estrutura de Testes

```
tests/
├── conftest.py              # Fixtures globais (db_session, client, app)
├── app/
│   ├── test_routes.py       # Testes de integração (rotas)
│   └── unit/
│       └── test_user_repository.py  # Testes unitários (repositórios)
```

**Tipos de testes:**

- **Unit**: Testam componentes isolados (repositórios, serviços)
- **Integration**: Testam a aplicação completa (rotas HTTP)

---

## ⚙️ Configuração

### **pytest.ini**

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
env =
    ENVIRONMENT=test
```

### **Variáveis de Ambiente**

Crie um arquivo `.env.test` ou configure:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/filmmash_test
ENVIRONMENT=test
```

---

## 🔬 Tipos de Testes

### **1. Testes Unitários (Repositórios)**

Testam a camada de dados isoladamente.

**Exemplo:** `tests/app/unit/test_user_repository.py`

```python
import pytest
from app.domains.auth.repositories.user_repository import UserRepository
from app.domains.auth.schemas import CreateUserDTO

class TestUserRepository:
    @pytest.fixture
    def user_repo(self, db_session):
        return UserRepository(db=db_session)

    @pytest.mark.asyncio
    async def test_create_user(self, user_repo):
        dto = CreateUserDTO(
            email="test@example.com",
            username="testuser",
            password_hash="hashed"
        )
        user = await user_repo.create(dto)
        assert user.email == "test@example.com"
```

---

### **2. Testes de Integração (Rotas)**

Testam a API completa (rotas HTTP).

**Exemplo:** `tests/app/test_routes.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_user_endpoint(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
```

---

## 🎯 Fixtures Disponíveis

As fixtures são componentes reutilizáveis para os testes. Elas estão definidas no `conftest.py`.

### **1. `test_engine`** (scope: session)

Engine do banco de dados para toda a sessão de testes.

```python
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(settings.database_url)
    yield engine
    await engine.dispose()
```

---

### **2. `db_session`** (scope: function)

Sessão isolada do banco com rollback automático.

**Como funciona:**
- Cada teste recebe uma transação limpa
- Ao final, faz rollback (nada persiste)
- Isolamento total entre testes

```python
@pytest.fixture
async def db_session(test_engine):
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
        await session.close()
        await trans.rollback()
```

**Uso:**

```python
async def test_example(db_session):
    # Use db_session para operações no banco
    result = await db_session.execute(select(User))
```

---

### **3. `app`** (scope: function)

Instância da aplicação FastAPI com dependências mockadas.

```python
@pytest.fixture
def app(db_session):
    app = create_app()
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_postgres_session] = override_get_db
    return app
```

**Uso:**

```python
def test_with_app(app):
    # app é uma instância do FastAPI
    assert app.title == "Filmmash API"
```

---

### **4. `client`** (scope: function)

Cliente HTTP para testes de integração.

```python
@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
```

**Uso:**

```python
async def test_api(client):
    response = await client.get("/api/v1/users")
    assert response.status_code == 200
```

---

## ✍️ Como Escrever Testes

### **Template Básico: Teste Unitário**

```python
import pytest
from uuid import uuid4
from app.domains.auth.repositories.user_repository import UserRepository
from app.domains.auth.schemas import CreateUserDTO

class TestUserRepository:
    @pytest.fixture
    def user_repo(self, db_session):
        """Cria o repositório para cada teste."""
        return UserRepository(db=db_session)

    @pytest.mark.asyncio
    async def test_create_user(self, user_repo):
        # Arrange (Preparar)
        dto = CreateUserDTO(
            email=f"test_{uuid4().hex[:8]}@example.com",
            username=f"user_{uuid4().hex[:8]}",
            password_hash="hashed"
        )

        # Act (Executar)
        user = await user_repo.create(dto)

        # Assert (Verificar)
        assert user is not None
        assert user.email == dto.email
        assert user.is_active is True
```

---

### **Template: Teste de Integração**

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    # Arrange
    payload = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "SecurePass123!"
    }

    # Act
    response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "password" not in data
```

---

### **Testando Exceções**

```python
import pytest
from app.db.exceptions import ResourceAlreadyExistsError

@pytest.mark.asyncio
async def test_create_duplicate_user(user_repo):
    dto = CreateUserDTO(email="same@example.com", username="same")

    await user_repo.create(dto)

    # Verifica que a segunda criação lança erro
    with pytest.raises(ResourceAlreadyExistsError):
        await user_repo.create(dto)
```

---

### **Fixtures Customizadas**

Crie fixtures específicas dentro do arquivo de teste:

```python
import pytest
from app.domains.auth.schemas import CreateUserDTO

@pytest.fixture
async def sample_user(user_repo):
    """Cria um usuário de exemplo para os testes."""
    dto = CreateUserDTO(
        email="sample@example.com",
        username="sampleuser",
        password_hash="hashed"
    )
    return await user_repo.create(dto)

@pytest.mark.asyncio
async def test_get_user(user_repo, sample_user):
    # sample_user já existe no banco
    found = await user_repo.get_by_id(sample_user.id)
    assert found is not None
```

---

## 🚀 Executando Testes

### **Rodar todos os testes**

```bash
pytest
```

### **Rodar um arquivo específico**

```bash
pytest tests/app/unit/test_user_repository.py
```

### **Rodar uma classe específica**

```bash
pytest tests/app/unit/test_user_repository.py::TestUserRepository
```

### **Rodar um teste específico**

```bash
pytest tests/app/unit/test_user_repository.py::TestUserRepository::test_create_user
```

### **Ver output detalhado**

```bash
pytest -v
```

### **Ver prints no console**

```bash
pytest -s
```

### **Rodar testes em paralelo**

```bash
pytest -n auto
```

### **Gerar relatório de cobertura**

```bash
pytest --cov=app --cov-report=html
```

---

## 📋 Boas Práticas

### **1. Padrão AAA (Arrange-Act-Assert)**

```python
async def test_example():
    # Arrange: Preparar dados
    dto = CreateUserDTO(...)

    # Act: Executar ação
    user = await repo.create(dto)

    # Assert: Verificar resultado
    assert user.email == dto.email
```

---

### **2. Nomes Descritivos**

✅ **Bom:**
```python
async def test_create_user_with_duplicate_email_raises_error()
```

❌ **Ruim:**
```python
async def test_user()
```

---

### **3. Isolamento de Testes**

- Cada teste deve ser independente
- Use `uuid4()` para gerar dados únicos
- Não dependa da ordem de execução

```python
# ✅ Dados únicos por teste
email = f"test_{uuid4().hex[:8]}@example.com"
```

---

### **4. Use Fixtures para Reutilização**

```python
@pytest.fixture
async def authenticated_client(client, sample_user):
    token = generate_token(sample_user)
    client.headers["Authorization"] = f"Bearer {token}"
    return client

async def test_protected_route(authenticated_client):
    response = await authenticated_client.get("/api/v1/me")
    assert response.status_code == 200
```

---

### **5. Teste Casos de Erro**

Não teste apenas o "caminho feliz":

```python
async def test_create_user_invalid_email(user_repo):
    dto = CreateUserDTO(email="invalid-email", ...)
    with pytest.raises(ValidationError):
        await user_repo.create(dto)
```

---

### **6. Organize por Classes**

```python
class TestUserRepository:
    """Agrupa testes relacionados."""

    async def test_create(self, user_repo): ...
    async def test_update(self, user_repo): ...
    async def test_delete(self, user_repo): ...
```

---

### **7. Coverage Mínimo: 80%**

```bash
pytest --cov=app --cov-report=term-missing
```

---

## 🎓 Próximos Passos

1. **Execute o teste exemplo:**
   ```bash
   pytest tests/app/unit/test_user_repository.py -v
   ```

2. **Crie testes para outros repositórios:**
   - `RoleRepository`
   - `PermissionRepository`
   - `SessionRepository`

3. **Escreva testes de integração para rotas:**
   - Login/Register
   - CRUD de usuários
   - Proteção por permissões

4. **Configure CI/CD:**
   - Execute testes automaticamente no GitHub Actions
   - Bloqueie merges se testes falharem

---

## 📚 Recursos Adicionais

- [Pytest Docs](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Testing](https://www.python-httpx.org/advanced/#calling-into-python-web-apps)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

---

**Dúvidas?** Consulte o time ou abra uma issue no repositório.
