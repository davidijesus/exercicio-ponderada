# Registro de Gastos Pessoais — API REST

Stack: **Python · FastAPI · SQLAlchemy · SQLite**

---

## Como rodar

```bash
pip install fastapi uvicorn sqlalchemy

cd expenses_api
python main.py
# → http://localhost:8080
# → http://localhost:8080/docs  (Swagger UI automático)
```

### Rodando os testes (sem banco real)
```bash
python tests/test_service.py
```

---

## Arquitetura em Camadas

```
main.py
  └── handler/expense_handler.py   ← HTTP ↔ Domínio
        └── service/expense_service.py  ← Regras de negócio
              └── repository/expense_repo.py  ← Persistência
                    └── domain/expense.py  ← Entidade + DTOs
```

Cada camada conhece **apenas a camada imediatamente abaixo**:

| Arquivo | Responsabilidade |
|---|---|
| `domain/expense.py` | `Expense`, DTOs, `ExpenseCategory` — não importa ninguém |
| `repository/expense_repo.py` | Interface + implementação SQLAlchemy |
| `service/expense_service.py` | Erros nomeados, validações, regras de negócio |
| `handler/expense_handler.py` | Tradução HTTP ↔ domínio, mapeamento erro → status |
| `main.py` | Composição: banco → repo → service → handler → rotas |

---

## Endpoints

| Método | Rota | Corpo | Respostas |
|---|---|---|---|
| POST | `/expenses/` | `{description, amount, category}` | 201 / 400 |
| GET | `/expenses/` | `?category=alimentacao` (opcional) | 200 / 400 |
| GET | `/expenses/:id` | — | 200 / 404 |
| PATCH | `/expenses/:id` | `{description?, amount?, category?}` | 200 / 400 / 404 |
| DELETE | `/expenses/:id` | — | 204 / 404 |

### Categorias válidas
`alimentacao` · `transporte` · `saude` · `educacao` · `outro`

---

## Respostas às Perguntas de Reflexão

### Tarefa 1 — Por que `ExpenseCategory` é um tipo nomeado?

Em Python, um `str` comum aceita qualquer valor: `"lazer"`, `"FOOD"`, `""` — tudo passa sem erro até chegar na validação manual. Ao usar `class ExpenseCategory(str, Enum)`, o sistema de tipos garante em tempo de execução que apenas os cinco valores definidos são aceitos. O `ValueError` do `Enum(value)` é lançado automaticamente para qualquer string inválida — sem nenhum `if` espalhado pelo código.

### Tarefa 1 — Por que o DTO de criação é separado da entidade?

Se o cliente pudesse enviar um `Expense` completo, poderia mandar:
- `"id": 42` → sobrescrevendo o ID de outro registro
- `"date": "2020-01-01"` → forjando uma data passada
- `"created_at": "..."` → manipulando o timestamp de auditoria

O `CreateExpenseRequest` expõe **apenas o que o cliente tem direito de definir**: `description`, `amount` e `category`. Os campos `id`, `date` e `created_at` são gerados exclusivamente pelo servidor — o cliente não tem nem como tentar enviá-los.

### Tarefa 2 — Trocar SQLite por PostgreSQL: quantos arquivos mudam?

**Apenas dois:**
1. `main.py` — 1 linha: a string de conexão (`sqlite:///./gastos.db` → `postgresql://user:pass@host/db`)
2. `repository/expense_repo.py` — possivelmente zero, ou ajustes pontuais de tipo (ex.: `Text` em vez de `String` para campos longos)

`service`, `handler` e `domain` não sabem que banco existe. Eles dependem da **interface `ExpenseRepository`**, não da implementação `SQLExpenseRepository`. Essa é a garantia da injeção de dependência: a regra de negócio não se importa com onde os dados estão guardados.
