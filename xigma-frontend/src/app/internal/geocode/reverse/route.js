const isValidCoordinate = (value, min, max) => {
  const number = Number(value);
  return Number.isFinite(number) && number >= min && number <= max;
};

export async function GET(request) {
  const apiKey = process.env.NESHAN_API_KEY;
  if (!apiKey) {
    return Response.json(
      { error: 'Reverse geocoding is not configured.' },
      { status: 503 },
    );
  }

  const { searchParams } = new URL(request.url);
  const lat = searchParams.get('lat');
  const lng = searchParams.get('lng');

  if (!isValidCoordinate(lat, -90, 90) || !isValidCoordinate(lng, -180, 180)) {
    return Response.json({ error: 'Invalid coordinates.' }, { status: 400 });
  }

  try {
    const upstreamUrl = new URL('https://api.neshan.org/v5/reverse');
    upstreamUrl.searchParams.set('lat', lat);
    upstreamUrl.searchParams.set('lng', lng);

    const response = await fetch(upstreamUrl, {
      headers: { 'Api-Key': apiKey },
      cache: 'no-store',
    });
    const data = await response.json();

    return Response.json(data, { status: response.status });
  } catch {
    return Response.json(
      { error: 'Reverse geocoding service is unavailable.' },
      { status: 502 },
    );
  }
}
