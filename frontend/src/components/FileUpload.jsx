import {
  useRef,
  useState
} from "react";

import {
  uploadDatabase
} from "../services/api";


function UploadIcon() {

  return (

    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M12 16V4" />
      <path d="m7 9 5-5 5 5" />
      <path d="M5 15v4h14v-4" />
    </svg>

  );
}


function FileUpload({
  onUploaded
}) {

  const inputRef =
    useRef(null);

  const [
    file,
    setFile
  ] = useState(null);

  const [
    uploading,
    setUploading
  ] = useState(false);

  const [
    message,
    setMessage
  ] = useState("");

  const [
    dragActive,
    setDragActive
  ] = useState(false);


  function selectFile(
    selectedFile
  ) {

    if (!selectedFile) {
      return;
    }

    setFile(
      selectedFile
    );

    setMessage("");
  }


  function handleDrop(
    event
  ) {

    event.preventDefault();

    setDragActive(false);

    selectFile(
      event.dataTransfer.files[0]
    );
  }


  async function handleUpload() {

    if (!file) {

      setMessage(
        "Choose a file first."
      );

      return;
    }


    try {

      setUploading(true);

      setMessage(
        "Importing dataset..."
      );


      const data =
        await uploadDatabase(
          file
        );


      setMessage(
        "Dataset imported successfully."
      );

      setFile(null);


      if (inputRef.current) {

        inputRef.current.value = "";

      }


      if (onUploaded) {

        onUploaded(
          data.database
        );

      }

    } catch (error) {

      setMessage(
        error.response?.data?.detail
        || "Unable to import this file."
      );

    } finally {

      setUploading(false);

    }
  }


  return (

    <div className="panel">

      <div className="panel-heading">

        <div className="panel-icon">

          <UploadIcon />

        </div>


        <div>

          <h3>
            Import data
          </h3>

          <p>
            Add your database or spreadsheet
          </p>

        </div>

      </div>


      <div
        className={
          `upload-dropzone ${
            dragActive
              ? "drag-active"
              : ""
          }`
        }
        onDragOver={(event) => {

          event.preventDefault();

          setDragActive(true);

        }}
        onDragLeave={() =>
          setDragActive(false)
        }
        onDrop={
          handleDrop
        }
        onClick={() =>
          inputRef.current?.click()
        }
      >

        <UploadIcon />

        <strong>

          Drop a file here

        </strong>

        <span>

          or click to browse

        </span>


        <small>

          SQLite, CSV or Excel · Max 20 MB

        </small>


        <input
          ref={
            inputRef
          }
          type="file"
          hidden
          accept=".db,.sqlite,.sqlite3,.csv,.xlsx"
          onChange={(event) =>
            selectFile(
              event.target.files[0]
            )
          }
        />

      </div>


      {file && (

        <div className="selected-file-card">

          <div>

            <span className="file-dot" />

            <div>

              <strong>
                {file.name}
              </strong>

              <span>
                {
                  (
                    file.size
                    / 1024
                    / 1024
                  ).toFixed(2)
                } MB
              </span>

            </div>

          </div>


          <button
            type="button"
            onClick={() =>
              setFile(null)
            }
          >
            ×
          </button>

        </div>

      )}


      <button
        className="import-button"
        onClick={
          handleUpload
        }
        disabled={
          uploading
          || !file
        }
      >

        {
          uploading
            ? (
              <>
                <span className="loader dark" />
                Importing
              </>
            )
            : "Import Dataset"
        }

      </button>


      {message && (

        <p className="upload-message">

          {message}

        </p>

      )}

    </div>
  );
}


export default FileUpload;