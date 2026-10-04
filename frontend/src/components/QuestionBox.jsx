import {
  useState
} from "react";


function ArrowIcon() {

  return (

    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M5 12h13" />
      <path d="m14 7 5 5-5 5" />
    </svg>

  );
}


function QuestionBox({
  database,
  onAsk,
  loading
}) {

  const [
    question,
    setQuestion
  ] = useState("");


  function handleSubmit(
    event
  ) {

    event.preventDefault();

    const cleanedQuestion =
      question.trim();

    if (!cleanedQuestion) {
      return;
    }

    onAsk(
      cleanedQuestion
    );
  }


  return (

    <div className="query-panel">

      <div className="query-heading">

        <div>

          <span className="mini-label">
            QUERY
          </span>

          <h3>
            Explore your data
          </h3>

          <p>
            Write your question the way
            you would normally ask it.
          </p>

        </div>


        {database && (

          <div className="active-database">

            <span />

            {database}

          </div>

        )}

      </div>


      {!database && (

        <div className="query-notice">

          Import or select a database
          before running an analysis.

        </div>

      )}


      <form
        onSubmit={
          handleSubmit
        }
      >

        <div className="question-field">

          <textarea
            rows="5"
            placeholder="Example: Which salesperson generated the highest total actual price?"
            value={
              question
            }
            onChange={(event) =>
              setQuestion(
                event.target.value
              )
            }
            disabled={
              !database
              || loading
            }
          />


          <div className="question-footer">

            <span className="character-count">

              {
                question.length
              } / 500

            </span>


            <button
              className="analysis-button"
              type="submit"
              disabled={
                !database
                || loading
                || !question.trim()
              }
            >

              {
                loading
                  ? (
                    <>
                      <span className="loader" />
                      Processing
                    </>
                  )
                  : (
                    <>
                      Run Analysis
                      <ArrowIcon />
                    </>
                  )
              }

            </button>

          </div>

        </div>

      </form>

    </div>
  );
}


export default QuestionBox;