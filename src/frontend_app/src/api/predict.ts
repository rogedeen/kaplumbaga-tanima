export async function predictImage(file: File) {
  const form = new FormData();
  form.append('image', file);

  const resp = await fetch('/api/predict', {
    method: 'POST',
    body: form,
  });

  if (!resp.ok) throw new Error('Prediction request failed');
  return resp.json();
}
