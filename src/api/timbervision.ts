const API_URL =
  "https://felixinberlin--timbervision-api-detector-detect.modal.run";


export async function detectTimber(image: File) {
  const formData = new FormData();

  formData.append("image_bytes", image);

  const response = await fetch(API_URL, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(
      `Detection failed: ${response.status}`
    );
  }

  return await response.json();
}