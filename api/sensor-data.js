/**
 * Vercel API Route - Receives sensor data from Raspberry Pi
 * Path: /api/sensor-data
 */

let sensorData = [];
let latestData = null;

export default function handler(req, res) {
  // Allow CORS
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, X-API-Key');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // POST: Receive data from Pi
  if (req.method === 'POST') {
    const apiKey = req.headers['x-api-key'];
    
    if (apiKey !== process.env.API_KEY) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const data = req.body;
    
    // Store latest data
    latestData = data;
    
    // Keep last 1000 readings
    sensorData.push({
      ...data,
      id: sensorData.length
    });
    
    if (sensorData.length > 1000) {
      sensorData = sensorData.slice(-1000);
    }

    return res.status(200).json({ success: true, message: 'Data received' });
  }

  // GET: Retrieve historical data
  if (req.method === 'GET') {
    const limit = req.query.limit || 100;
    const sensorId = req.query.sensor; // Optional: filter by sensor
    
    let result = sensorData.slice(-limit);
    
    if (sensorId) {
      result = result.map(d => ({
        timestamp: d.timestamp,
        sensor: d.sensors[`sensor_${sensorId}`],
        id: d.id
      }));
    }

    return res.status(200).json({
      latest: latestData,
      history: result,
      total: sensorData.length
    });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
