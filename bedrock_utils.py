import os
import json
import re
from dotenv import load_dotenv
import boto3

load_dotenv()

def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION"))

def get_sql_from_nl(nl_query, table_schema):
    """
    Sends a natural language question and schema to Claude 3.7 via Bedrock,
    and extracts the SQL query from the response.
    """
    bedrock = get_bedrock_client()

    # Construct the user prompt for Claude
    user_prompt = (
        f"You are a SQL expert. Convert the following natural language question into a valid SQL query "
        f"based on this SQLite schema:\n\n{table_schema}\n\n"
        f"Question: {nl_query}"
    )

    body = {
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0.5
    }

    # Invoke Claude 3.7 via inference profile
    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_MODEL_ID"),
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    # Extract Claude response content
    raw_response = result["content"][0]["text"].strip()

    # Try to extract SQL code block from ```sql ... ```
    match = re.search(r"```sql(.*?)```", raw_response, re.DOTALL | re.IGNORECASE)

    if match:
        sql_query = match.group(1).strip()
    else:
        # Fall back to returning the entire response if no SQL block found
        sql_query = raw_response

    return sql_query
