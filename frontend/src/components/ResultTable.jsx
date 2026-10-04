function ResultTable({
  result
}) {

  if (!result) {
    return null;
  }


  return (

    <div className="result-panel">

      {/* Answer */}

      <div className="result-header">

        <div>

          <span className="mini-label">
            RESULT
          </span>

          <h3>
            Analysis summary
          </h3>

        </div>


        <div className="result-status">

          <span />

          Complete

        </div>

      </div>


      <div className="answer-block">

        <div className="answer-mark">

          “

        </div>

        <p>
          {result.answer}
        </p>

      </div>


      {/* RAG Tables */}

      {
        result.relevant_tables?.length
        > 0
        && (

          <div className="source-row">

            <span>
              Referenced
            </span>

            {
              result.relevant_tables.map(
                (table) => (

                  <span
                    className="source-chip"
                    key={
                      table
                    }
                  >
                    {table}
                  </span>

                )
              )
            }

          </div>

        )
      }


      {/* Result Table */}

      {
        result.columns?.length
        > 0
        && (

          <div className="data-section">

            <div className="data-section-heading">

              <h4>
                Query result
              </h4>

              <span>

                {
                  result.rows.length
                } {
                  result.rows.length === 1
                    ? "row"
                    : "rows"
                }

              </span>

            </div>


            <div className="table-wrapper">

              <table>

                <thead>

                  <tr>

                    {
                      result.columns.map(
                        (
                          column,
                          index
                        ) => (

                          <th
                            key={
                              `${column}-${index}`
                            }
                          >
                            {column}
                          </th>

                        )
                      )
                    }

                  </tr>

                </thead>


                <tbody>

                  {
                    result.rows.map(
                      (
                        row,
                        rowIndex
                      ) => (

                        <tr
                          key={
                            rowIndex
                          }
                        >

                          {
                            row.map(
                              (
                                value,
                                columnIndex
                              ) => (

                                <td
                                  key={
                                    columnIndex
                                  }
                                >

                                  {
                                    value
                                    === null
                                      ? "—"
                                      : String(
                                          value
                                        )
                                  }

                                </td>

                              )
                            )
                          }

                        </tr>

                      )
                    )
                  }

                </tbody>

              </table>

            </div>

          </div>

        )
      }


      {result.truncated && (

        <div className="limit-notice">

          Showing the first 200 rows.

        </div>

      )}


      {/* SQL */}

      {result.sql && (

        <details className="query-details">

          <summary>

            View technical query

          </summary>

          <div className="sql-block">

            <code>
              {result.sql}
            </code>

          </div>

        </details>

      )}

    </div>
  );
}


export default ResultTable;