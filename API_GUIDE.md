# Baby Cry Reason Detection API - Integration Guide

This guide explains how to integrate the Baby Cry Reason Detection API into your own projects (Mobile Apps, Web Frontends, or other Backends).

## 1. Quick Info
- **Base URL**: `http://localhost:8000` (Update this to your production URL)
- **Endpoint**: `/api/v1/predict/`
- **Method**: `POST`
- **Auth Header**: `X-API-KEY`
- **Body Format**: `multipart/form-data`

## 2. Authentication
Every request must include the `X-API-KEY` in the HTTP header. 
If you are using the default development key, it is:
`dev-api-key-change-in-production`

## 3. Integration Examples

### JavaScript (Fetch API)
```javascript
const formData = new FormData();
formData.append('audio', audioFile); // audioFile must be a .wav Blob or File

const response = await fetch('http://localhost:8000/api/v1/predict/', {
    method: 'POST',
    headers: {
        'X-API-KEY': 'your_api_key_here'
    },
    body: formData
});

const data = await response.json();
console.log(`Prediction: ${data.label} (${data.confidence * 100}%)`);
```

### Python (Requests)
```python
import requests

url = "http://localhost:8000/api/v1/predict/"
headers = {"X-API-KEY": "your_api_key_here"}
files = {"audio": open("cry_sample.wav", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

### Dart / Flutter (Dio)
```dart
import 'package:dio/dio.dart';

var dio = Dio();
FormData formData = FormData.fromMap({
  "audio": await MultipartFile.fromFile("./cry_sample.wav", filename: "cry.wav"),
});

var response = await dio.post(
  "http://localhost:8000/api/v1/predict/",
  data: formData,
  options: Options(headers: {"X-API-KEY": "your_api_key_here"}),
);
print(response.data);
```

## 4. Response Structure

### Success (200 OK)
```json
{
  "label": "hungry",
  "confidence": 0.9842,
  "reason": "The acoustic pattern shows rhythmic, repeated 'neh' sounds...",
  "probabilities": {
    "belly_pain": 0.0012,
    "burping": 0.0005,
    "discomfort": 0.0041,
    "hungry": 0.9842,
    "tired": 0.0100
  }
}
```

### Possible Predicted Labels
- `hungry`: Needs feeding.
- `belly_pain`: Digestive discomfort or gas.
- `burping`: Needs to be burped.
- `discomfort`: Environmental or physical irritation.
- `tired`: Needs sleep.

## 5. Error Codes
| Code | Meaning | Solution |
| :--- | :--- | :--- |
| **400** | Missing Field | Ensure the file is sent with the key name `audio`. |
| **401** | Unauthorized | Check your `X-API-KEY` header. |
| **405** | Wrong Method | Ensure you are using `POST`. |
| **415** | Format Error | Ensure the file extension is `.wav`. |
| **422** | Audio Error | The audio is silent or corrupted. Try a better sample. |

## 6. Optimization Tips
- **Duration**: The model is optimized for 4-second clips. If sending longer audio, consider trimming it to the first 4-5 seconds of actual crying.
- **Audio Profile**: 22050Hz Mono is the native format; higher quality files are accepted but will be downsampled by the server.
- **Latency**: The model is kept in memory (singleton). You don't need to worry about "cold starts" during consecutive requests.
