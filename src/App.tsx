import { useState } from "react"

function App() {
  const [preview, setPreview] = useState<string | null>(null)
  const [fileType, setFileType] = useState<string>("")

  function handleFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]

    if (!file) return

    setFileType(file.type)

    const url = URL.createObjectURL(file)
    setPreview(url)
  }

  return (
    <div>
      <header>
        <h1>TimberVision Upload</h1>
      </header>

      <main>
        <label>
          Upload image or video

          <input
            type="file"
            accept="image/*,video/*"
            capture="environment"
            onChange={handleFile}
          />
        </label>

        {preview && (
          <div>
            <p>{fileType}</p>

            {fileType.startsWith("image") && (
              <img
                src={preview}
                style={{ maxWidth: "100%" }}
              />
            )}

            {fileType.startsWith("video") && (
              <video
                src={preview}
                controls
                style={{ maxWidth: "100%" }}
              />
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App