const DETECT_URL =
  "https://felixinberlin--timbervision-api-detector-detect.modal.run";

const CALCULATE_URL =
  "https://felixinberlin--timbervision-api-calculate.modal.run";


export async function detectTimber(
  image: File
) {

  const formData = new FormData();

  formData.append(
    "image_bytes",
    image
  );


  const response = await fetch(
    DETECT_URL,
    {
      method: "POST",
      body: formData
    }
  );


  if (!response.ok) {
    throw new Error(
      "Detection failed"
    );
  }


  return response.json();
}



export async function calculateTimber(
  detectionResult: any
) {

  const response = await fetch(
    CALCULATE_URL,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(
        detectionResult
      )
    }
  );


  if (!response.ok) {
    throw new Error(
      "Calculation failed"
    );
  }


  return response.json();
}