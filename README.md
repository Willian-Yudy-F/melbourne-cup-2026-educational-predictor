# Melbourne Cup 2026 — Educational Probability Project

Projeto educacional em Python para transformar um snapshot público de candidatos e
cotações do Melbourne Cup 2026 em probabilidades reproduzíveis e auditáveis.

> **Não é dica de aposta.** Leia o [DISCLAIMER.md](DISCLAIMER.md). O campo final de até
> 24 cavalos e as barreiras serão definidos em 31 de outubro de 2026. O snapshot usado
> aqui é anterior ao campo final e foi observado em 22 de outubro de 2026.

## Projeção provisória

As tabelas geradas ficam em:

- [`outputs/melbourne_cup_2026_projection.csv`](outputs/melbourne_cup_2026_projection.csv)
- [`outputs/melbourne_cup_2026_projection.md`](outputs/melbourne_cup_2026_projection.md)

O ranking principal é o **cenário educacional**, não uma recomendação. A coluna
`market_baseline_probability` é a referência mais neutra: probabilidade implícita das
cotações, normalizada entre os candidatos acompanhados.

## O que usamos

- Python 3.11+
- `pandas` para ingestão, validação e tabelas
- `numpy` para normalização probabilística
- `pytest` para testes de integridade
- Git e GitHub para versionamento e documentação
- Fontes públicas da VRC, Racing Victoria e um snapshot agregado de cotações

Este repositório é uma adaptação responsável do pipeline maior de previsão de corridas.
Não aplicamos o modelo XGBoost treinado em dados sintéticos aos cavalos reais: isso
produziria uma falsa sensação de precisão. O código mantém o mesmo desenho de produção
— snapshot datado, validação, features explícitas, inferência e artefatos versionados —
mas usa uma baseline transparente enquanto não há um dataset histórico real licenciado.

## Como fizemos

1. Registramos um snapshot dos candidatos com nome, treinador, peso, cotação atual,
   cotação anterior e situação de vaga garantida.
2. Validamos duplicatas, valores ausentes, cotações maiores que 1 e pesos plausíveis.
3. Calculamos a baseline `1 / decimal_odds` e removemos a margem normalizando a soma.
4. Criamos um cenário didático com ajustes deliberadamente pequenos:
   - peso: `exp(-0.018 × (peso - peso_médio))`;
   - movimento: `(cotação_anterior / cotação_atual)^0.15`, limitado a `[0.85, 1.15]`;
   - vaga garantida: multiplicador `1.03`.
5. Normalizamos novamente para que as probabilidades somem 100%.
6. Exportamos CSV e Markdown e testamos os invariantes.

Esses coeficientes são hipóteses didáticas, não parâmetros aprendidos. O mercado já
incorpora parte dessas informações, portanto existe risco de dupla contagem. A saída
mostra baseline e cenário lado a lado para tornar isso visível.

## Executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
pytest -q
```

Para usar outro snapshot:

```bash
python main.py --input data/melbourne_cup_2026_candidates.csv --output-dir outputs
```

## Estrutura

```text
data/                         snapshot versionado
src/melbourne_cup/            validação e projeção
outputs/                      tabelas geradas
tests/                        testes dos invariantes
main.py                       CLI
METHODOLOGY.md                detalhes e limitações
DISCLAIMER.md                 finalidade educacional
```

## Fontes e data de corte

- [Victoria Racing Club — 58 horses remain, 13 Oct 2026](https://www.vrc.com.au/latest-news/58-horses-remain-in-the-race-for-cup-glory/)
- [VRC — Point Of Law earns a Golden Ticket, 21 Oct 2026](https://www.vrc.com.au/latest-news/point-of-law-earns-golden-ticket-into-the-2026-lexus-melbourne-cup/)
- [Racing Victoria — Feature Race Conditions and Order of Entry](https://www.racingvictoria.com.au/racing/feature-race-conditions)
- [Race.com.au — market snapshot and weights, 22 Oct 2026](https://race.com.au/melbourne-cup/)

As cotações são voláteis e foram transcritas apenas para este exercício. Não há coleta
automática de sites de apostas, nem afiliação com as fontes. Consulte sempre as fontes
oficiais para aceitações e condições da corrida.

## Próximos passos técnicos

- Atualizar o snapshot após o campo final e sorteio das barreiras em 31 de outubro.
- Ingerir resultados históricos reais com licença adequada.
- Usar validação temporal por ano e calibração fora da amostra.
- Adicionar forma recente, distância, pista, jóquei e handicap sem vazamento temporal.
- Publicar intervalos de incerteza e relatório de calibração.

