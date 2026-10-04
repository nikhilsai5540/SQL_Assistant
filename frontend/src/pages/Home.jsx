import {
  useEffect,
  useState,
} from "react";

import FileUpload
  from "../components/FileUpload";

import QuestionBox
  from "../components/QuestionBox";

import ResultTable
  from "../components/ResultTable";

import {
  askQuestion,
  getDatabases,
  getSchema,
} from "../services/api";


/* =========================================================
   Database Icon
========================================================= */

function DatabaseIcon() {

  return (

    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >

      <ellipse
        cx="12"
        cy="5"
        rx="7"
        ry="3"
      />

      <path
        d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5"
      />

      <path
        d="M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"
      />

    </svg>

  );
}


/* =========================================================
   Structure Icon
========================================================= */

function StructureIcon() {

  return (

    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >

      <rect
        x="3"
        y="4"
        width="7"
        height="6"
        rx="1.5"
      />

      <rect
        x="14"
        y="4"
        width="7"
        height="6"
        rx="1.5"
      />

      <rect
        x="8.5"
        y="15"
        width="7"
        height="5"
        rx="1.5"
      />

      <path
        d="M6.5 10v2.5h11V10"
      />

      <path
        d="M12 12.5V15"
      />

    </svg>

  );
}


/* =========================================================
   Home Page
========================================================= */

function Home() {

  const [
    databases,
    setDatabases
  ] = useState([]);

  const [
    selectedDatabase,
    setSelectedDatabase
  ] = useState("");

  const [
    result,
    setResult
  ] = useState(null);

  const [
    loading,
    setLoading
  ] = useState(false);

  const [
    error,
    setError
  ] = useState("");

  const [
    schema,
    setSchema
  ] = useState(null);


  /* =====================================================
     Load databases when page starts
  ===================================================== */

  useEffect(() => {

    loadDatabases();

  }, []);


  /* =====================================================
     Load Databases
  ===================================================== */

  async function loadDatabases(
    preferredDatabase = null
  ) {

    try {

      const data =
        await getDatabases();

      const items =
        data.databases || [];

      setDatabases(items);


      if (preferredDatabase) {

        setSelectedDatabase(
          preferredDatabase
        );

      }

      else if (
        items.length > 0
        && !selectedDatabase
      ) {

        setSelectedDatabase(
          items[0].name
        );

      }

    }

    catch (error) {

      setError(
        "Unable to connect to the backend service."
      );

    }

  }


  /* =====================================================
     After File Upload
  ===================================================== */

  async function handleUploaded(
    databaseName
  ) {

    await loadDatabases(
      databaseName
    );

    setResult(null);

    setSchema(null);

    setError("");

  }


  /* =====================================================
     Ask Question
  ===================================================== */

  async function handleAsk(
    question
  ) {

    if (!selectedDatabase) {
      return;
    }


    try {

      setError("");

      setResult(null);

      setLoading(true);


      const data =
        await askQuestion(
          selectedDatabase,
          question
        );


      setResult(data);

    }

    catch (error) {

      setError(
        error.response?.data?.detail
        ||
        "The request could not be processed."
      );

    }

    finally {

      setLoading(false);

    }

  }


  /* =====================================================
     View Database Schema
  ===================================================== */

  async function handleViewSchema() {

    if (!selectedDatabase) {
      return;
    }


    try {

      setError("");


      const data =
        await getSchema(
          selectedDatabase
        );


      setSchema(data);

    }

    catch (error) {

      setError(
        error.response?.data?.detail
        ||
        "Unable to load the database structure."
      );

    }

  }


  /* =====================================================
     UI
  ===================================================== */

  return (

    <div className="app-shell">


      {/* =================================================
          Header
      ================================================= */}

      <header className="topbar">

        <div className="brand">


          {/* Logo */}

          <div className="brand-mark">

            D

          </div>


          {/* Project Name */}

          <div>

            <h1>
              DataLens
            </h1>

            <p>
              Natural language database explorer
            </p>

          </div>

        </div>


        {/* Status */}

        <div className="workspace-status">

          <span
            className="status-dot"
          />

          Local workspace

        </div>

      </header>


      {/* =================================================
          Hero Section
      ================================================= */}

      <section className="intro-section">

        <div>

          <span className="eyebrow">

            DATA WORKSPACE

          </span>


          <h2>

            Ask your data.

            <br />

            Get clear answers.

          </h2>


          <p>

            Import a dataset,
            choose your database
            and explore it using
            everyday language.

          </p>

        </div>

      </section>


      {/* =================================================
          Main Workspace
      ================================================= */}

      <main className="workspace-grid">


        {/* =================================================
            LEFT SIDE
        ================================================= */}

        <aside className="workspace-sidebar">


          {/* Workspace Heading */}

          <div className="section-heading">

            <span>
              Workspace
            </span>

            <span
              className="section-line"
            />

          </div>


          {/* =================================================
              Upload Dataset
          ================================================= */}

          <FileUpload

            onUploaded={
              handleUploaded
            }

          />


          {/* =================================================
              Database Selection
          ================================================= */}

          <div className="panel">


            <div className="panel-heading">


              <div className="panel-icon">

                <DatabaseIcon />

              </div>


              <div>

                <h3>

                  Active database

                </h3>

                <p>

                  Choose the dataset
                  to explore

                </p>

              </div>


            </div>


            {/* Database Dropdown */}

            {

              databases.length === 0

              ? (

                <div className="empty-small">

                  No databases
                  available yet.

                </div>

              )

              : (

                <select

                  className="database-select"

                  value={
                    selectedDatabase
                  }

                  onChange={(event) => {

                    setSelectedDatabase(
                      event.target.value
                    );

                    setResult(null);

                    setSchema(null);

                    setError("");

                  }}

                >


                  {

                    databases.map(
                      (database) => (

                        <option

                          key={
                            database.name
                          }

                          value={
                            database.name
                          }

                        >

                          {
                            database.name
                          }

                        </option>

                      )
                    )

                  }


                </select>

              )

            }


            {/* View Structure Button */}

            <button

              className="outline-button"

              onClick={
                handleViewSchema
              }

              disabled={
                !selectedDatabase
              }

            >

              <StructureIcon />

              View database structure

            </button>


          </div>


          {/* =================================================
              Database Schema
          ================================================= */}

          {

            schema && (

              <div className="panel schema-panel">


                <div className="panel-title-row">


                  <div>

                    <span className="mini-label">

                      STRUCTURE

                    </span>

                    <h3>

                      Tables & columns

                    </h3>

                  </div>


                  <span className="count-pill">

                    {
                      schema.tables.length
                    }

                  </span>


                </div>


                <div className="schema-list">


                  {

                    schema.tables.map(
                      (table) => (

                        <div

                          className="schema-table"

                          key={
                            table.name
                          }

                        >


                          {/* Table Name */}

                          <div className="schema-table-name">

                            <DatabaseIcon />

                            <span>

                              {
                                table.name
                              }

                            </span>

                          </div>


                          {/* Columns */}

                          <div className="schema-columns">


                            {

                              table.columns.map(
                                (column) => (

                                  <div

                                    key={
                                      column.name
                                    }

                                    className="schema-column"

                                  >


                                    <span>

                                      {
                                        column.name
                                      }

                                    </span>


                                    <span className="column-type">

                                      {
                                        column.type
                                      }

                                    </span>


                                  </div>

                                )
                              )

                            }


                          </div>


                        </div>

                      )
                    )

                  }


                </div>


              </div>

            )

          }


        </aside>


        {/* =================================================
            RIGHT SIDE
        ================================================= */}

        <section className="analysis-area">


          {/* Analysis Heading */}

          <div className="section-heading">

            <span>
              Analysis
            </span>

            <span
              className="section-line"
            />

          </div>


          {/* =================================================
              Question Area
          ================================================= */}

          <QuestionBox

            database={
              selectedDatabase
            }

            loading={
              loading
            }

            onAsk={
              handleAsk
            }

          />


          {/* =================================================
              Error
          ================================================= */}

          {

            error && (

              <div className="error-message">


                <span className="error-symbol">

                  !

                </span>


                <div>


                  <strong>

                    Unable to complete request

                  </strong>


                  <p>

                    {
                      error
                    }

                  </p>


                </div>


              </div>

            )

          }


          {/* =================================================
              Empty / Welcome State
          ================================================= */}

          {

            !result
            &&
            !loading
            &&
            !error
            &&
            (

              <div className="welcome-panel">


                <div className="welcome-symbol">

                  <DatabaseIcon />

                </div>


                <h3>

                  Ready when you are

                </h3>


                <p>

                  Select a database
                  and enter a question
                  above to begin exploring
                  your data.

                </p>


                {/* Example Questions */}

                <div className="example-area">


                  <span>

                    Try asking

                  </span>


                  <div className="example-questions">


                    {/* Example 1 */}

                    <button

                      type="button"

                      onClick={() =>
                        handleAsk(
                          "Which salesperson generated the highest total actual price?"
                        )
                      }

                      disabled={
                        !selectedDatabase
                      }

                    >

                      Highest performing salesperson

                    </button>


                    {/* Example 2 */}

                    <button

                      type="button"

                      onClick={() =>
                        handleAsk(
                          "Show total actual price by region."
                        )
                      }

                      disabled={
                        !selectedDatabase
                      }

                    >

                      Compare sales by region

                    </button>


                    {/* Example 3 */}

                    <button

                      type="button"

                      onClick={() =>
                        handleAsk(
                          "What is the average actual price?"
                        )
                      }

                      disabled={
                        !selectedDatabase
                      }

                    >

                      Find average actual price

                    </button>


                  </div>


                </div>


              </div>

            )

          }


          {/* =================================================
              Result
          ================================================= */}

          <ResultTable

            result={
              result
            }

          />


        </section>


      </main>


      {/* =================================================
          Footer
      ================================================= */}

      <footer className="page-footer">


        <span>

          QuerySlate

        </span>


        <span>

          Natural language database workspace

        </span>


      </footer>


    </div>

  );

}


export default Home;