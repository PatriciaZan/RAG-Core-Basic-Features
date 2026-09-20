"""
Templates de prompts otimizados para consultas SQL.
Evita confusão entre tabelas e melhora qualidade das queries.
"""

import json
from typing import Optional


class PromptBuilder:
    """Builder para construir prompts otimizados para IA gerar SQL."""
    def __init__(self, database_schema: dict, relationships: dict):
        """
        Args:
            database_schema: Schema melhorado com context
            relationships: Relacionamentos entre tabelas
        """
        self.schema = database_schema
        self.relationships = relationships

    def build(self) -> str:
        """
        Cria o prompt de SISTEMA que define o comportamento.

        Returns:
            String com instrções do sistema
        """
        return """Você é um especialista em SQL com profundo conhecimento de um banco de dados de negócios.

## RESPONSABILIDADE PRINCIPAL
Gerar queries SQL precisas que consultam a tabela CORRETA (não confundir tabelas similares).

## REGRAS CRÍTICAS DE DISAMBIGUAÇÃO

### 1. PRODUCTS vs SALES (A confusão mais comum!)
- **PRODUCTS**: Catálogo MASTER (o que PODE ser vendido)
  - Procure por: características, features, preço padrão, SLA, responsável técnico
  - Responda sobre: "O que é o produto?" "Quais features?" "Qual preço?"

- **SALES**: Histórico de TRANSAÇÕES (o que FOI vendido)
  - Procure por: quantidades vendidas, receita, quando vendeu, quem comprou
  - Responda sobre: "Quantas vendas?" "Receita?" "Tendências?"

### 2. Regra de Ouro
Se a pergunta faz sentido com "quantidade de vendas" → USE SALES
Se a pergunta faz sentido com "características técnicas" → USE PRODUCTS

### 3. Quando JOINear
- Sales + Products = informações de venda + detalhes do produto
- Sales + Customers = informações de venda + dados do cliente
- Sales + Stores = informações de venda + localização

### 4. ANTES de escrever SQL
SEMPRE explique em comentários:
- Qual tabela é a fonte de verdade para essa pergunta
- Por que essa tabela
- Se precisa de JOIN e por quê

## FORMATO DE RESPOSTA OBRIGATÓRIO

```
**Análise:**
[Explicar qual tabela é certa e por que]

**Tabelas utilizadas:**
[Listar tabelas e motivo]

**Query SQL:**
```sql
[SQL aqui]
```

**Validação:**
[Confirmar que query responde a pergunta original]
```

## REGRAS ADICIONAIS

1. Sempre use aliases para tabelas (p = products, s = sales, c = customers)
2. Prefira INNER JOIN quando há relacionamento direto
3. Use LEFT JOIN quando você quer incluir registros sem match
4. Ordene por relevância (DESC para valores, ASC para datas antigas)
5. Coloque LIMIT se retorna muitos resultados
6. Use COUNT() e SUM() para agregações
7. Sempre GROUP BY quando usa agregações
8. Nomes de colunas: use aspas duplas em PostgreSQL se necessário
"""

    def build_context_block(self, include_examples: bool = True) -> str:
        """
        Cria o bloco de contexto com schema e exemplos.

        Args:
            include_examples: Se deve incluir exemplos de queries certas/erradas

        Returns:
            String com contexto formatado
        """
        context = "## DATABASE SCHEMA\n\n"

        # Adicionar cada tabela com suas informações
        for table_name, table_info in self.schema.items():
            emoji = table_info.get("emoji", "📋")
            label = table_info.get("label", table_name)
            purpose = table_info.get("purpose", "")
            type_desc = table_info.get("type", "")

            context += f"""
### {emoji} {label}
- **Tipo**: {type_desc}
- **Purpose**: {purpose}
- **Chave primária**: {table_info.get("primary_key", "N/A")}

**Usar quando pergunta sobre:**
"""
            use_when = table_info.get("use_this_table_when_question_asks_about", [])
            for item in use_when[:5]:  # Primeiros 5
                context += f"  - {item}\n"

            # Adicionar disambiguação se houver
            dont_confuse = table_info.get("do_NOT_confuse_with", {})
            if dont_confuse:
                context += "\n**NÃO confundir com:**\n"
                for other_table, explanation in dont_confuse.items():
                    context += f"  - {other_table}: {explanation[:100]}...\n"

            context += "\n"

        if include_examples:
            context += self._build_examples_block()

        return context

    def _build_examples_block(self) -> str:
        """Cria bloco de exemplos de queries certas/erradas."""
        return """
## EXEMPLOS DE QUERIES CERTAS E ERRADAS

###  ERRADO: Confundir PRODUCTS com SALES
**Pergunta**: "Quais são os produtos mais vendidos?"

**Query ERRADA** (consultando PRODUCTS sem JOIN):
```sql
SELECT name, standalone_monthly_price_brl 
FROM products 
ORDER BY name 
LIMIT 10;
--  Retorna apenas lista de produtos, não vendas!
```

**Query CORRETA** (usando SALES + JOIN):
```sql
SELECT 
    p.product_id,
    p.name,
    COUNT(s.sale_id) as total_vendas,
    SUM(s.amount_brl) as receita_total
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id, p.name
ORDER BY total_vendas DESC
LIMIT 10;
--  Conta quantas vendas cada produto teve
```

###  ERRADO: Confundir CUSTOMERS com SALES
**Pergunta**: "Quanto cada cliente gastou?"

**Query ERRADA** (apenas CUSTOMERS):
```sql
SELECT customer_id, company_name, mrr 
FROM customers;
--  MRR é receita MENSAL do cliente, não o que gastou em vendas
```

**Query CORRETA** (usando SALES + GROUP BY):
```sql
SELECT 
    c.customer_id,
    c.company_name,
    COUNT(s.sale_id) as total_compras,
    SUM(s.amount_brl) as total_gasto
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.company_name
ORDER BY total_gasto DESC;
--  Soma todas as vendas de cada cliente
```

###  CERTO: Usar tabela certa
**Pergunta**: "Quais são os features do produto X?"

```sql
SELECT 
    name,
    category,
    features,
    supported_os,
    sla_uptime
FROM products
WHERE product_id = 'payment-gateway';
--  PRODUCTS tem features e características
```

###  CERTO: JOINear quando necessário
**Pergunta**: "Qual foi a receita de cada cliente em setembro?"

```sql
SELECT 
    c.customer_id,
    c.company_name,
    COUNT(s.sale_id) as num_vendas,
    SUM(s.amount_brl) as receita_setembro
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
WHERE EXTRACT(MONTH FROM s.date) = 9
    AND EXTRACT(YEAR FROM s.date) = 2024
GROUP BY c.customer_id, c.company_name
ORDER BY receita_setembro DESC;
--  JOIN customers + sales, filtra por data
```
"""

    def build_full_prompt(
            self,
            user_question: str,
            include_examples: bool = True,
            additional_context: Optional[str] = None
    ) -> str:
        """
        Monta o prompt completo (system + context + pergunta do usuário).

        Args:
            user_question: A pergunta do usuário
            include_examples: Se deve incluir exemplos
            additional_context: Contexto adicional (ex: filtros temporais)

        Returns:
            Prompt completo formatado
        """
        prompt = ""

        # Sistema + Context
        prompt += self.build_system_prompt()
        prompt += "\n" + "=" * 80 + "\n"
        prompt += self.build_context_block(include_examples)

        # Contexto adicional se houver
        if additional_context:
            prompt += f"\n## CONTEXTO ADICIONAL\n{additional_context}\n"

        # Pergunta do usuário
        prompt += f"\n## PERGUNTA DO USUÁRIO\n{user_question}\n"

        # Instruções finais
        prompt += """
## AGORA SIGA ESTES PASSOS:

1. **Identifique** qual tabela é fonte de verdade
2. **Explique** por que essa tabela
3. **Mostre** a query SQL
4. **Valide** que a query responde a pergunta

Lembre-se: Se fez a pergunta ao banco e está confuso qual tabela usar,
a resposta provavelmente está ERRADA. Volte aos princípios acima.
"""

        return prompt

    def explain_table_choice(self, user_question: str) -> str:
        """
        Explica qual tabela deveria ser usada (helper para debugging).

        Args:
            user_question: A pergunta do usuário

        Returns:
            Recomendação de qual tabela usar
        """
        question_lower = user_question.lower()

        # Keywords que indicam SALES
        sales_keywords = [
            "quantas", "quantidade", "vendida", "vendas", "receita",
            "gasto", "comprou", "transação", "venda", "tendência",
            "performance", "faturamento", "revenue", "sold"
        ]

        # Keywords que indicam PRODUCTS
        products_keywords = [
            "produto", "features", "característica", "preço",
            "descrição", "categoria", "sla", "uptime",
            "tech lead", "product manager", "o que é"
        ]

        # Contar matches
        sales_matches = sum(1 for kw in sales_keywords if kw in question_lower)
        products_matches = sum(1 for kw in products_keywords if kw in question_lower)

        if sales_matches > products_matches:
            return (
                f"✓ Pareça uma pergunta sobre SALES\n"
                f"  Cause: Encontradas keywords: "
                f"{[kw for kw in sales_keywords if kw in question_lower]}\n"
                f"  Use a tabela SALES (+ JOIN com PRODUCTS se precisar de detalhes)"
            )
        elif products_matches > sales_matches:
            return (
                f"✓ Parece uma pergunta sobre PRODUCTS\n"
                f"  Cause: Encontradas keywords: "
                f"{[kw for kw in products_keywords if kw in question_lower]}\n"
                f"  Use a tabela PRODUCTS"
            )
        else:
            return (
                f"⚠ Pergunta ambígua. Revise a próxima seção sobre "
                f"SALES vs PRODUCTS para decidir."
            )

