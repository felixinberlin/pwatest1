import { useState } from "react";
import { detectTimber } from "../api/timbervision";


export default function ImageDetector() {

  const [image, setImage] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);


  async function handleDetect() {

    if (!image) return;

    setLoading(true);

    try {

      const data = await detectTimber(image);

      setResult(data);

    } catch (error) {

      console.error(error);
      alert("Detection failed");

    } finally {

      setLoading(false);

    }
  }


  return (
    <div>

      <input
        type="file"
        accept="image/*"
        onChange={(e) =>
          setImage(e.target.files?.[0] ?? null)
        }
      />


      <button
        disabled={!image || loading}
        onClick={handleDetect}
      >
        {loading
          ? "Analyzing..."
          : "Detect timber"}
      </button>


      {result && (
        <pre>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}

    </div>
  );
}