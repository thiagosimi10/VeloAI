# 21-RAG.md

> Projeto → VeloAI
> Documento → Arquitetura RAG (Retrieval-Augmented Generation)
> Módulo → Inteligência Artificial
> Versão → 1.0.0

---

# Objetivo

O RAG (Retrieval-Augmented Generation) será o cérebro de conhecimento do VeloAI.

Seu objetivo será permitir que a IA responda perguntas utilizando informações reais da empresa, documentos enviados pelos usuários, configurações do sistema, histórico de conversas e dados estruturados, sempre respeitando o isolamento entre Tenants.

A IA nunca responderá baseada apenas no conhecimento do modelo quando a resposta depender de informações da empresa.

Sempre que necessário deverá consultar o RAG.

---

# Filosofia

Nunca inventar informações.

Sempre consultar documentos.

Sempre consultar dados da empresa.

Sempre citar a origem da informação quando possível.

Sempre respeitar o isolamento entre empresas.

---

# Fluxo Geral

```text
Usuário

↓

Pergunta

↓

Planner Agent

↓

Verifica necessidade de contexto

↓

RAG

↓

Busca Vetorial

↓

Ranking

↓

Contexto

↓

LLM

↓

Resposta
```

---

# Stack

LLM.

Gemini 3.1 Flash Lite.

Embeddings.

Gemini Embedding API.

Banco Vetorial.

PostgreSQL + pgvector.

Framework.

FastAPI.

Chunking.

LangChain Text Splitters.

Parser.

Unstructured.

OCR.

Tesseract.

PDF.

PyMuPDF.

Word.

python-docx.

Excel.

openpyxl.

CSV.

Pandas.

---

# Fontes de Conhecimento

Documentos PDF.

Contratos.

Manuais.

Catálogos.

Planilhas.

Imagens.

Notas Fiscais.

Documentação Técnica.

Perguntas Frequentes.

Políticas da Empresa.

Configurações.

Histórico da IA.

Conversas.

Resultados anteriores.

---

# Dados Estruturados

Além dos documentos.

O RAG poderá consultar.

Clientes.

Produtos.

Ordens de Serviço.

Vendas.

Financeiro.

Agenda.

Relatórios.

Dashboards.

Sempre através das MCP Tools.

Nunca diretamente.

---

# Pipeline de Indexação

```text
Upload

↓

Validação

↓

Extração

↓

OCR (quando necessário)

↓

Limpeza

↓

Normalização

↓

Chunking

↓

Embeddings

↓

pgvector

↓

Indexação
```

---

# Uploads Suportados

PDF.

DOCX.

TXT.

CSV.

XLSX.

PNG.

JPG.

JPEG.

WEBP.

Markdown.

HTML.

JSON.

XML.

---

# OCR

Executar automaticamente quando.

Documento escaneado.

Imagem.

PDF sem texto.

Extrair.

Texto.

Tabelas.

Campos.

Assinaturas quando possível.

---

# Chunking

Estratégia padrão.

Chunk Size.

1000 caracteres.

Overlap.

200 caracteres.

Nunca gerar chunks gigantes.

Nunca gerar chunks extremamente pequenos.

---

# Metadados

Cada Chunk armazenará.

ID.

Tenant.

Documento.

Autor.

Tipo.

Data.

Versão.

Hash.

Idioma.

Categoria.

Origem.

Tags.

Permissões.

---

# Estrutura da Tabela

```text
ai_embeddings

id

tenant_id

document_id

chunk_index

content

embedding

model

metadata

created_at

updated_at
```

---

# Busca Vetorial

Sempre utilizar.

Cosine Similarity.

Top K.

Re-ranking.

Filtros.

Threshold mínimo.

---

# Estratégia de Busca

Fluxo.

```text
Pergunta

↓

Embedding

↓

Busca Vetorial

↓

Top 20

↓

Re-ranking

↓

Top 5

↓

Contexto Final
```

---

# Re-ranking

Critérios.

Similaridade.

Recência.

Tipo do documento.

Prioridade.

Permissões.

Categoria.

Score.

---

# Contexto

Limitar.

Número máximo de chunks.

Quantidade máxima de tokens.

Eliminar duplicidades.

Ordenar por relevância.

---

# Cache

Criar.

Prompt Cache.

Embedding Cache.

Search Cache.

Resposta Cache.

Sempre invalidar quando documentos forem atualizados.

---

# Atualização

Sempre que documento mudar.

Reindexar apenas os chunks alterados.

Nunca reindexar tudo sem necessidade.

---

# Versionamento

Cada documento possuirá.

Versão.

Histórico.

Data.

Autor.

Hash.

A IA sempre utilizará a versão mais recente.

---

# Exclusão

Soft Delete.

Remover do índice vetorial.

Manter histórico para auditoria.

---

# Isolamento

Cada Tenant possuirá.

Embeddings próprios.

Documentos próprios.

Índice próprio.

Nunca misturar dados.

Nunca permitir consultas cruzadas.

---

# Segurança

Validar.

Tenant.

Usuário.

Permissões.

Categoria.

Documento.

Antes de retornar qualquer contexto.

---

# IA

O Planner Agent decidirá.

Quando utilizar o RAG.

Quando utilizar MCP.

Quando utilizar ambos.

Quando responder diretamente.

---

# Exemplos

Pergunta.

```
Qual é a política de garantia da minha empresa?
```

↓

Consulta RAG.

↓

Retorna documento.

↓

Resposta.

---

Pergunta.

```
Qual produto mais vendeu em maio?
```

↓

Executa MCP.

↓

Consulta banco.

↓

Resposta.

---

Pergunta.

```
Qual o procedimento de troca e quantas trocas ocorreram este mês?
```

↓

Consulta RAG.

↓

Consulta MCP.

↓

Combina resultados.

↓

Resposta.

---

# Indexação Automática

Ao enviar um documento.

Executar.

Extração.

OCR.

Chunking.

Embeddings.

Indexação.

Auditoria.

Tudo automaticamente.

---

# Auditoria

Registrar.

Documento.

Chunks.

Modelo.

Tempo.

Usuário.

Tenant.

Quantidade de Tokens.

---

# Logs

Registrar.

Busca.

Score.

Chunks utilizados.

Tempo.

Modelo.

Tokens.

Resultado.

---

# Observabilidade

Monitorar.

Tempo médio.

Precisão.

Quantidade de documentos.

Embeddings.

Consultas.

Cache Hit.

Cache Miss.

---

# APIs

```
POST /rag/upload

POST /rag/search

POST /rag/reindex

GET /rag/documents

GET /rag/document/{id}

DELETE /rag/document/{id}

POST /rag/rebuild-index
```

---

# MCP Tools

IndexDocument.

SearchKnowledge.

DeleteDocument.

ReindexDocument.

SummarizeDocument.

ExtractDocumentMetadata.

SearchSimilarDocuments.

---

# Performance

Processamento Assíncrono.

Celery.

Redis.

Batch Embeddings.

Lazy Loading.

Compressão.

Cache.

---

# Testes

Cobertura mínima.

95%.

Testar.

Upload.

OCR.

Chunking.

Embeddings.

Busca Vetorial.

Permissões.

Tenant.

Cache.

Reindexação.

---

# Roadmap

Adicionar.

Hybrid Search.

Knowledge Graph.

GraphRAG.

Multi Modal RAG.

Voice RAG.

Image Search.

Code Search.

Video Search.

Incremental Embeddings.

Modelos Locais.

---

# Regras Obrigatórias

Nunca responder utilizando informações desatualizadas.

Nunca responder utilizando documentos de outro Tenant.

Sempre registrar auditoria.

Sempre utilizar embeddings atualizados.

Sempre validar permissões.

Sempre remover documentos excluídos do índice.

Sempre registrar versão do documento utilizado.

---

# Objetivo Final

O RAG do VeloAI será a principal fonte de conhecimento contextual da plataforma. Ele permitirá que a IA responda perguntas baseadas em documentos reais da empresa, combinando busca vetorial, MCP, dados estruturados e histórico de interações. Toda a arquitetura deverá priorizar precisão, segurança, desempenho e isolamento total entre Tenants, transformando a IA em um verdadeiro especialista no contexto de cada empresa.

---
