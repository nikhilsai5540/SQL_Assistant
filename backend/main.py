from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from database import (
    get_database_path,
    list_databases,
    save_uploaded_database,
)

from schema_reader import get_database_schema

from rag_retriever import retrieve_relevant_schema

from sql_generator import (
    generate_sql,
    repair_sql,
)

from sql_validator import validate_sql

from query_executor import execute_query

from answer_generator import generate_answer


# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(
    title="RAG SQL Assistant",
    description="Natural Language to SQL using RAG + Ollama",
    version="1.0.0",
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Request Models
# =====================================================

class QuestionRequest(BaseModel):

    database: str

    question: str = Field(
        min_length=2,
        max_length=500,
    )


# =====================================================
# Home API
# =====================================================

@app.get("/")
def home():

    return {
        "message": "RAG SQL Assistant API is running.",
        "status": "success",
    }


# =====================================================
# Get Available Databases
# =====================================================

@app.get("/api/databases")
def databases():

    try:

        database_list = list_databases()

        return {
            "databases": database_list
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load databases: {error}",
        )


# =====================================================
# Upload Database
# =====================================================

@app.post("/api/upload")
async def upload_database(
    file: UploadFile = File(...)
):

    try:

        # ---------------------------------------------
        # Check filename
        # ---------------------------------------------

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="File name is missing.",
            )

        # ---------------------------------------------
        # Read uploaded file
        # ---------------------------------------------

        content = await file.read()

        # Maximum file size = 20 MB

        maximum_size = (
            20 * 1024 * 1024
        )

        if len(content) > maximum_size:

            raise HTTPException(
                status_code=400,
                detail=(
                    "File is too large. "
                    "Maximum size is 20 MB."
                ),
            )

        # ---------------------------------------------
        # Save / Convert Database
        # ---------------------------------------------

        database_name = save_uploaded_database(
            file.filename,
            content,
        )

        return {
            "message":
                "Database uploaded successfully.",

            "database":
                database_name,
        }

    except HTTPException:

        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {error}",
        )


# =====================================================
# View Database Schema
# =====================================================

@app.get(
    "/api/databases/{database_name}/schema"
)
def database_schema(
    database_name: str
):

    try:

        # ---------------------------------------------
        # Find Database
        # ---------------------------------------------

        database_path = get_database_path(
            database_name
        )

        # ---------------------------------------------
        # Read Schema
        # ---------------------------------------------

        schema = get_database_schema(
            database_path
        )

        return {
            "database":
                database_name,

            "tables":
                schema,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to read schema: {error}",
        )


# =====================================================
# Ask Database using Natural Language
# =====================================================

@app.post("/api/ask")
def ask_database(
    request: QuestionRequest
):

    try:

        print("\n")
        print("=" * 60)
        print("NEW QUESTION")
        print("=" * 60)

        print(
            f"Database: {request.database}"
        )

        print(
            f"Question: {request.question}"
        )

        # =================================================
        # STEP 1
        # Find selected database
        # =================================================

        database_path = get_database_path(
            request.database
        )


        # =================================================
        # STEP 2
        # RAG retrieves relevant tables/schema
        # =================================================

        schema_context, relevant_tables = (
            retrieve_relevant_schema(
                database_path,
                request.question,
                top_k=3,
            )
        )

        print("\nRelevant Tables:")

        print(
            ", ".join(relevant_tables)
        )


        # =================================================
        # STEP 3
        # Generate SQL using Ollama
        # =================================================

        generated_sql = generate_sql(
            request.question,
            schema_context,
        )


        # ---------------------------------------------
        # Cannot Answer
        # ---------------------------------------------

        if (
            generated_sql
            == "CANNOT_ANSWER"
        ):

            return {
                "question":
                    request.question,

                "answer":
                    (
                        "I cannot answer this question "
                        "from the available database schema."
                    ),

                "sql":
                    None,

                "columns":
                    [],

                "rows":
                    [],

                "relevant_tables":
                    relevant_tables,

                "truncated":
                    False,
            }


        # =================================================
        # STEP 4
        # Validate generated SQL
        # =================================================

        safe_sql = validate_sql(
            generated_sql
        )

        print("\n")
        print("=" * 60)
        print("GENERATED SQL")
        print("=" * 60)

        print(safe_sql)


        # =================================================
        # STEP 5
        # Execute SQL
        # =================================================

        try:

            result = execute_query(
                database_path,
                safe_sql,
            )

            print("\nSQL executed successfully.")


        # =================================================
        # If SQL failed:
        # Ask Ollama to repair query automatically
        # =================================================

        except ValueError as execution_error:

            print("\n")
            print("=" * 60)
            print("SQL EXECUTION FAILED")
            print("=" * 60)

            print(execution_error)


            print("\n")
            print(
                "Trying automatic SQL repair..."
            )


            # ---------------------------------------------
            # Generate repaired SQL
            # ---------------------------------------------

            repaired_sql = repair_sql(
                question=request.question,
                schema_context=schema_context,
                previous_sql=safe_sql,
                sqlite_error=str(
                    execution_error
                ),
            )


            # ---------------------------------------------
            # Validate repaired SQL
            # ---------------------------------------------

            safe_sql = validate_sql(
                repaired_sql
            )


            print("\n")
            print("=" * 60)
            print("REPAIRED SQL")
            print("=" * 60)

            print(safe_sql)


            # ---------------------------------------------
            # Execute repaired SQL
            # ---------------------------------------------

            result = execute_query(
                database_path,
                safe_sql,
            )


            print(
                "\nRepaired SQL executed successfully."
            )


        # =================================================
        # STEP 6
        # Generate Natural-Language Answer
        # =================================================

        answer = generate_answer(
            request.question,
            result["columns"],
            result["rows"],
        )


        # =================================================
        # STEP 7
        # Send Response to React
        # =================================================

        response = {

            "question":
                request.question,

            "answer":
                answer,

            "sql":
                safe_sql,

            "columns":
                result["columns"],

            "rows":
                result["rows"],

            "relevant_tables":
                relevant_tables,

            "truncated":
                result["truncated"],
        }


        print("\n")
        print("=" * 60)
        print("ANSWER")
        print("=" * 60)

        print(answer)

        print("\n")
        print("=" * 60)


        return response


    # =====================================================
    # Ollama connection/model errors
    # =====================================================

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


    # =====================================================
    # SQL/schema/database errors
    # =====================================================

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    # =====================================================
    # Unexpected Errors
    # =====================================================

    except Exception as error:

        print(
            f"\nUnexpected server error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Server error: {error}",
        )