import requests
import json
import datetime
from ast import literal_eval

def review_code():    
    url = "http://ollama-service:11434/api/chat"
    

    context = get_context()
    planning_rules = get_planning_rules()
    format_rules = get_format_rules()
    instruction = "Review this code for me"
    code = get_code_for_review()
    request_content = f"""
    <context>{context}</context>
    <planning_rules>{planning_rules}</planning_rules>
    <format_rules>{format_rules}</format_rules>
    {instruction}
    <code>
    {code}
    </code>
    """

    payload = {
        "model": "deepseek-r1:14b",
        "messages": [
            {"role": "user", "content": request_content}
        ],
        "stream": False
    }
    response = requests.post(url, json=payload)
    print(response.status_code)    # e.g. 200 if successful
    # print(response.text)           # the raw text output
    data = response.json()
    # print(data)
    model = data['model']
    created_at = data['created_at']
    message = data['message']
    role = message['role']
    content = message['content']
    done_reason = data['done_reason']
    done = data['done']
    total_duration = data['total_duration']
    load_duration = data['load_duration']
    prompt_eval_count = data['prompt_eval_count']
    eval_count = data['eval_count']
    eval_duration = data['eval_duration']

    print(f'model            :{model}')
    print(f'total_duration   :{total_duration}')
    print(f'prompt_eval_count: {prompt_eval_count}')
    print(f'eval_count       : {eval_count}')
    print()
    print(content)


    


    """
    curl http://localhost:11434/api/chat -d '{
    "model": "deepseek-r1",
    "messages": [{ "role": "user", "content": "Solve: 25 * 25" }],
    "stream": false
    }'
    """

    """
    <context>
    You are a senior software engineer specializing in debugging. Analyze error messages, identify root causes, and provide concise fixes. Prioritize solutions that prevent recurrence.
    </context>

    <planning_rules>
    - Reproduce the error locally first
    - Isolate the faulty component
    - Test the fix in a sandboxed environment
    </planning_rules>

    <format_rules>
    - Present errors as: [ERROR TYPE]: [DESCRIPTION]
    - Explain causes in plain English
    - Offer code snippets with before/after comparisons
    </format_rules>
    """


    """
    <!-- from https://www.youtube.com/watch?app=desktop&v=kRXfddrtrmM -->
    **Instruction**: {instruction}

    **Goal**: {goal}

    **Model settings**:
    - Temperature: 0.7
    - Max tokens: 300
    """

    """
    <think>
    A successful product launch email  should be clear , engaging, and action orientated.
    It should introduce the product, highlight key benefits and encourage the reader to engage.
    A semi-formal tone balances professionalism with approachability.
    </think>
    <answer>
    Write a concise, semi-formal email introducing a new product.
    - open with an engaging hook.
    - Highlight key features and benefits.
    - Include clear call to action (e.g. website link, sign up, purchase).
    - Keep tone professional yet approachable.
    </answer>
    """

    

    
def get_context():
    return "You are a senior software engineer specializing in SQL and Data Engineering. Analyze code for semantic, stylistic and syntactical issues. Provide specific steps to remediate poor code."

def get_planning_rules():
    return """
        - Ensure SQL is suitable for PostgreSQL
        - Favour CTEs over subqueries
        - Keywords should be in lower case
        - Object names such as tables, views and columns should be in upper case.
        """

def get_format_rules():
    return "Return output in markdown."

def get_code_for_review():
    return """
--What does it do
--Why does it do that (who for, when etc)
    --Should it do it ;-) [Delete, Update, Add]
--How does it do it
    --How do make it "do it" better? (faster, cheaper, safer, more repeatable...)
--Is it correct?

with
chu_recent_inhouse_big_win_plays as (
    SELECT distinct
        cast(SOURCE_PLAY_ID AS STRING) as PLAY_ID,
        TRANSACTION_USALA_DATE_KEY,
        cast(dg.GAME_NAME AS STRING)   AS GAME_NAME
    FROM
        CHU_PROD.CURATED.FACT_CHUMBA_PLAYS fcp
            LEFT JOIN CHU_PROD.CURATED.DIM_GAME dg
                      ON fcp.GAME_KEY = dg.PK
    WHERE
          TRANSACTION_USALA_DATE_KEY >= '2024-01-01'

    --BUG: Wouldn't find plays that won 10k
    -- over multiple spins for the same play i.e. 2k+4k+5k
      AND WIN_AMOUNT / 100 >= 100000
    ),
    chu_recent_ris_big_win_plays     as (
        SELECT distinct
            cast(SOURCE_ID AS STRING)    as PLAY_ID,
            TRANSACTION_USALA_DATE_KEY,
            cast(dg.GAME_NAME AS STRING) AS GAME_NAME
        FROM
            CHU_PROD.CURATED.FACT_RGS_PLAYS fgp
                LEFT JOIN CHU_PROD.CURATED.DIM_GAME dg
                          ON fgp.GAME_KEY = dg.PK
        WHERE
              TRANSACTION_USALA_DATE_KEY >= '2024-01-01'

              --BUG: Wouldn't find plays that won 10k over multiple spins for the same play i.e. 2k+4k+5k
          AND WIN_AMOUNT / 100 >= 100000
        ),
    chu_winners                      AS (
        SELECT
            'CHU'                            AS BRAND_CODE,
            f.TRANSACTION_USALA_DATE_KEY     AS DATE,
            cast(d.USER_ID AS STRING)        AS USER_ID,
            ifnull(avtd.MAX_VALUE_TIER, 1)   AS TIER_JACKPOT_WIN,-- Tier at the time player won
            cast(f.SOURCE_PLAY_ID AS STRING) AS PLAY_ID,
            sum(f.PLAY_AMOUNT) / 100         AS SC_PLAY_AMOUNT,  -- Sum because we want to see the initial play amt even if player won on free spin, play_id is shared
            sum(f.WIN_AMOUNT) / 100          AS SC_WIN_AMOUNT,   -- Reporting on entire play not spin
            cast(dg.GAME_NAME AS STRING)     AS GAME_NAME
        FROM
            CHU_PROD.CURATED.FACT_CHUMBA_PLAYS f
                LEFT JOIN  CHU_PROD.CURATED.DIM_PLAYER d
                           ON f.PLAYER_KEY = d.PK
                LEFT JOIN  CAM_PROD.CURATED.ACCOUNT_VALUE_TIER_DAILY avtd
                           ON cast(d.USER_ID AS STRING) = cast(avtd.ACCOUNT_ID AS STRING)
                               AND TRANSACTION_USALA_DATE_KEY = avtd.VALUE_TIER_DATE
                               AND avtd.PRODUCT = 'CHU'
                LEFT JOIN  CHU_PROD.CURATED.DIM_GAME dg
                           ON f.GAME_KEY = dg.PK
                               -- Filtering on any play_id with a >100K Win, we want to sum the entire win amount and play amount, accounts for free spins
                INNER JOIN chu_recent_inhouse_big_win_plays f2
                           ON f.TRANSACTION_USALA_DATE_KEY = f2.TRANSACTION_USALA_DATE_KEY
                               AND cast(f.SOURCE_PLAY_ID AS STRING) = cast(f2.PLAY_ID AS STRING)
                               AND cast(dg.GAME_NAME AS STRING) = cast(f2.GAME_NAME AS STRING)
        WHERE
              f.TRANSACTION_USALA_DATE_KEY >= '2024-01-01'
          AND f.COIN_TYPE_KEY = 2
        GROUP BY
            f.TRANSACTION_USALA_DATE_KEY,
            cast(d.USER_ID AS STRING),
            ifnull(avtd.MAX_VALUE_TIER, 1),
            cast(f.SOURCE_PLAY_ID AS STRING),
            cast(dg.GAME_NAME AS STRING)
        union all
        SELECT
            'CHU'                          AS BRAND_CODE,
            fg.TRANSACTION_USALA_DATE_KEY  AS DATE,
            cast(d.USER_ID AS STRING)      AS USER_ID,
            ifnull(avtd.MAX_VALUE_TIER, 1) AS TIER_JACKPOT_WIN,-- Tier at the time player won
            cast(fg.SOURCE_ID AS STRING)   AS PLAY_ID,
            sum(fg.PLAY_AMOUNT) / 100      AS SC_PLAY_AMOUNT,
            sum(fg.WIN_AMOUNT) / 100       AS SC_WIN_AMOUNT,
            cast(dg.GAME_NAME AS STRING)   AS GAME_NAME
        FROM
            CHU_PROD.CURATED.FACT_RGS_PLAYS fg
                LEFT JOIN  CHU_PROD.CURATED.DIM_PLAYER d
                           ON fg.PLAYER_KEY = d.PK
                LEFT JOIN  CAM_PROD.CURATED.ACCOUNT_VALUE_TIER_DAILY avtd
                           ON cast(d.USER_ID AS STRING) = cast(avtd.ACCOUNT_ID AS STRING)
                               AND TRANSACTION_USALA_DATE_KEY = avtd.VALUE_TIER_DATE
                               AND avtd.PRODUCT = 'CHU'
                LEFT JOIN  CHU_PROD.CURATED.DIM_GAME dg
                           ON fg.GAME_KEY = dg.PK
                INNER JOIN chu_recent_ris_big_win_plays f2
                           ON fg.TRANSACTION_USALA_DATE_KEY = f2.TRANSACTION_USALA_DATE_KEY
                               AND cast(fg.SOURCE_ID AS STRING) = cast(f2.PLAY_ID AS STRING)
                               AND cast(dg.GAME_NAME AS STRING) = cast(f2.GAME_NAME AS STRING)
        WHERE
              fg.TRANSACTION_USALA_DATE_KEY >= '2024-01-01'
          AND fg.COIN_TYPE_KEY = 2
        GROUP BY
            fg.TRANSACTION_USALA_DATE_KEY,
            cast(d.USER_ID AS STRING),
            ifnull(avtd.MAX_VALUE_TIER, 1),
            cast(fg.SOURCE_ID AS STRING),
            cast(dg.GAME_NAME AS STRING)
        )
        ,
    lls_recent_big_win_plays         as (
        SELECT distinct
            cast(ifnull(play_id, player_id) AS STRING) as PLAY_ID,
            LLS_DATE_USALA,
            cast(MACHINE_ID AS STRING)                 AS GAME_NAME
        FROM
            LLS_PROD.CURATED.plays
        WHERE
              LLS_DATE_USALA >= '2024-01-01'
          AND CURRENCY_WON / 100 >= 100000
          AND CURRENCY_TYPE = 'sweeps'
        ),
    lls_winners                      AS (
        SELECT
            'LLS'                                              AS BRAND_CODE,
            p.LLS_DATE_USALA                                   AS DATE,
            cast(p.PLAYER_ID AS STRING)                     AS USER_ID,
            ifnull(v.NET_PURCHASE_MAX_TIER, 1)                AS TIER_JACKPOT_WIN,
            cast(ifnull(p.play_id, p.player_id) AS STRING) AS PLAY_ID,
            sum(p.CURRENCY_WAGERED) / 100                  AS SC_PLAY_AMOUNT,
            sum(p.CURRENCY_WON) / 100                      AS SC_WIN_AMOUNT,
            cast(p.MACHINE_ID AS STRING)                    AS GAME_NAME
        FROM
            LLS_PROD.CURATED.plays p
                LEFT JOIN  CAM_PROD.CURATED.V_ACCOUNT_MANAGEMENT_TIER_DETAILS v
                           ON cast(p.USER_ID AS STRING) = cast(v.ACCOUNT_ID AS STRING)
                               AND p.LLS_DATE = v.DATE_UTC
                               AND v.PRODUCT = 'LLS'
                INNER JOIN lls_recent_big_win_plays f
                           ON p.LLS_DATE_USALA = f.LLS_DATE_USALA
                               AND
                              cast(ifnull(p.play_id, p.player_id) AS STRING) = cast(f.PLAY_ID AS STRING)
                               AND cast(p.MACHINE_ID AS STRING) = cast(f.GAME_NAME AS STRING)
        WHERE
              p.CURRENCY_TYPE = 'sweeps'
          AND p.LLS_DATE_USALA >= '2024-01-01'
        GROUP BY
            p.LLS_DATE_USALA,
            cast(p.PLAYER_ID AS STRING),
            ifnull(v.NET_PURCHASE_MAX_TIER, 1),
            cast(ifnull(p.play_id, p.player_id) AS STRING),
            cast(p.MACHINE_ID AS STRING)
        )
        ,
    pok_winners                      AS (
        SELECT
            'POK'                               AS BRAND_CODE,
            date(v.DATETIME_UTC)                AS DATE,
            cast(v.USER_ID AS STRING)           AS USER_ID,
            ifnull(t.max_amt_tier, 1)           AS TIER_JACKPOT_WIN,
            cast(v.GAME_INSTANCE_ID as STRING)  AS PLAY_ID,
            sum(v.AMOUNT_PLAYED)                AS SC_PLAY_AMOUNT,
            sum(v.AMOUNT_WON)                   AS SC_WIN_AMOUNT,
            cast(v.GAME_NAME AS STRING)         AS GAME_NAME
        FROM
            POK_PROD.CURATED.V_UNIFIED_PLAYS v
                LEFT JOIN  (
                               SELECT
                                   DATE(
                                           DATEADD(
                                                   'MONTH', 1, month)) AS date_month,
                                   'POK'                               AS brand_code,
                                   CAST(
                                           user_id AS STRING)          AS account_id,
                                   --In GP a players tier remains static the entire month
                                   CASE
                                       WHEN segment = 'Tier 7' THEN 7
                                       WHEN segment = 'Tier 6' THEN 6
                                       WHEN segment = 'Tier 5' THEN 5
                                       WHEN segment = 'Tier 4' THEN 4
                                       WHEN segment = 'Tier 3' THEN 3
                                       WHEN segment = 'Tier 2' THEN 2
                                       WHEN segment = 'Tier 1' THEN 1
                                       ELSE 0 END                      AS max_amt_tier
                               FROM
                                   POK_PROD.CURATED.V_VALUE_SEGMENTS
                               WHERE
                                   month >= '2023-12-01'
                               ) t
                           ON cast(
                                      v.USER_ID AS STRING) = cast(
                                      t.account_id AS STRING)
                               AND date_trunc(
                                           'month', date(
                                               v.DATETIME_UTC)) = t.date_month
                INNER JOIN (
                               SELECT distinct
                                   cast(GAME_INSTANCE_ID as STRING) as PLAY_ID,
                                   date(DATETIME_UTC)               AS DATE,
                                   cast(GAME_NAME AS STRING)        AS GAME_NAME
                               FROM
                                   POK_PROD.CURATED.V_UNIFIED_PLAYS
                               WHERE
                                     date(DATETIME_UTC) >= '2024-01-01'
                                 AND COIN_TYPE = 'SC'
                                 AND AMOUNT_WON >= 100000
                               ) f
                           ON date(v.DATETIME_UTC) = f.DATE
                               AND cast(v.GAME_INSTANCE_ID as STRING) = cast(f.PLAY_ID AS STRING)
                               AND cast(v.GAME_NAME AS STRING) = cast(f.GAME_NAME AS STRING)
        WHERE
              date(v.DATETIME_UTC) >= '2024-01-01'
          AND v.COIN_TYPE = 'SC'
        GROUP BY
            date(v.DATETIME_UTC),
            cast(v.USER_ID AS STRING),
            ifnull(t.max_amt_tier, 1),
            cast(v.GAME_INSTANCE_ID as STRING),
            cast(v.GAME_NAME AS STRING)
        )
        ,
    all_winners                      AS (
        SELECT *
        FROM
            chu_winners
        UNION ALL
        SELECT *
        FROM
            lls_winners
        UNION ALL
        SELECT *
        FROM
            pok_winners
        )
        ,
    distinct_winners                 AS ( -- used to filter player list
        select distinct
            CAST(
                    user_id AS STRING) AS USER_ID,
            BRAND_CODE
        from
            all_winners
        )
        ,
    player_state                     AS
        (
        SELECT
            cast(
                    chupok.account_id AS STRING) AS ACCOUNT_ID,
            chupok.BRAND_CODE,
            chupok.STATE
        FROM
            (
                SELECT
                    CAST(
                            S.account_id AS STRING) AS ACCOUNT_ID,
                    s.BRAND_CODE,
                    UPPER(
                            state)                  AS STATE,
                    address_type,
                    type_rank
                FROM
                    (
                        SELECT
                            'CHU'                         as brand_code,
                            cast(
                                    account_id AS STRING) as account_id,
                            address_type,
                            --CDD is most trusted, then SDD and then billing
                            CASE
                                WHEN address_type = 'CDD' THEN 1
                                WHEN address_type = 'SDD' THEN 2
                                WHEN address_type = 'Billing (Bank)' THEN 3
                                ELSE 4 END                AS type_rank,
                            ADDRESS_SUBDIVISION_CODE      AS state,
                            valid_from_timestamp_utc,
                            valid_to_timestamp_utc
                        FROM
                            CHU_PROD.CURATED.V_ACCOUNT_CONTACT_ADDRESS
                        --Latest state per address_type entry method (SDD, CDD, Billing)
                        QUALIFY
                            (
                                ROW_NUMBER(
                                ) OVER (
                                    PARTITION BY account_id, address_type ORDER BY valid_from_timestamp_utc DESC)) =
                            1
                        UNION ALL
                        SELECT
                            'POK'                         as brand_code,
                            cast(
                                    account_id AS STRING) as account_id,
                            address_type,
                            --CDD is most trusted, then SDD and then billing
                            CASE
                                WHEN address_type = 'CDD' THEN 1
                                WHEN address_type = 'SDD' THEN 2
                                WHEN address_type = 'Billing (Bank)' THEN 3
                                ELSE 4 END                AS type_rank,
                            ADDRESS_SUBDIVISION_CODE      AS state,
                            valid_from_timestamp_utc,
                            VALID_TILL_TIMESTAMP_UTC
                        FROM
                            POK_PROD.CURATED.V_ACCOUNT_CONTACT_ADDRESS
                        --Latest state per address_type entry method (SDD, CDD, Billing)
                        QUALIFY
                            (
                                ROW_NUMBER(
                                ) OVER (
                                    PARTITION BY account_id, address_type ORDER BY valid_from_timestamp_utc DESC)) =
                            1
                        ) s
                        INNER JOIN distinct_winners dw
                                   ON cast(
                                              s.account_id AS STRING) = cast(
                                              dw.USER_ID as STRING)
                                       AND s.brand_code = dw.brand_code
                --Return the most trusted available state based information per user
                QUALIFY
                    (
                        ROW_NUMBER(
                        ) OVER (
                            PARTITION BY s.brand_code, account_id ORDER BY type_rank)) = 1
                ) chupok
        UNION ALL
        SELECT -- LLS has GEO code only
               cast(v.ACCOUNT_ID AS STRING) AS ACCOUNT_ID,
               'LLS'                           AS BRAND_CODE,
               v.GEO_LOCATION_SUBDIVISION_CODE AS STATE
        FROM
            LLS_PROD.CURATED.V_IDENTITY_LOGIN v
                INNER JOIN distinct_winners dw
                           ON cast(
                                      v.account_id AS STRING) = cast(
                                      dw.USER_ID as STRING)
        QUALIFY
            (ROW_NUMBER() OVER (PARTITION BY ACCOUNT_ID ORDER BY LOGIN_TIMESTAMP_UTC DESC)) = 1
        )
        ,
    winners_final                    AS (
        SELECT
            aw.BRAND_CODE,
            DATE,
            cast(USER_ID AS STRING)   AS user_id,
            cast(ps.STATE AS STRING)  AS STATE,
            TIER_JACKPOT_WIN,
            cast(PLAY_ID AS STRING)   AS PLAY_ID,
            SC_PLAY_AMOUNT,
            SC_WIN_AMOUNT,
            cast(GAME_NAME AS STRING) AS GAME_NAME
        FROM
            all_winners aw
                LEFT JOIN player_state ps
                          ON cast(aw.USER_ID AS STRING) = cast(ps.account_id AS STRING)
                              AND aw.brand_code = ps.brand_code
        )

SELECT
    "BRAND_CODE"       AS "BRAND_CODE",
    "DATE"             AS "DATE",
    "GAME_NAME"        AS "GAME_NAME",
    "PLAY_ID"          AS "PLAY_ID",
    "SC_PLAY_AMOUNT"   AS "SC_PLAY_AMOUNT",
    "SC_WIN_AMOUNT"    AS "SC_WIN_AMOUNT",
    "STATE"            AS "STATE",
    "TIER_JACKPOT_WIN" AS "TIER_JACKPOT_WIN",
    "USER_ID"          AS "USER_ID"
from
    winners_final;

    """

if __name__ == "__main__":
    review_code()