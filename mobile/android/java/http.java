	private static final int TIMEOUT_MILLISEC = 1000;

	public static void sendDataToHTTPService(String URL, HashMap<String, String> data)
	{
	  try {
	        JSONObject json = new JSONObject();

	        for (Map.Entry<String, String> entry : data.entrySet()) 
	        { 
	        	json.put(entry.getKey(), entry.getValue());
        	}
	        HttpParams httpParams = new BasicHttpParams();
	        HttpConnectionParams.setConnectionTimeout(httpParams, TIMEOUT_MILLISEC);
	        HttpConnectionParams.setSoTimeout(httpParams, TIMEOUT_MILLISEC);
	        HttpClient client = new DefaultHttpClient(httpParams);

	        HttpPost request = new HttpPost(URL);
	        request.setEntity(new ByteArrayEntity(json.toString().getBytes("UTF8")));
	        request.setHeader("json", json.toString());
	        HttpResponse response = client.execute(request);
	        HttpEntity entity = response.getEntity();

	        if (entity != null) {
	            InputStream instream = entity.getContent();

	            String result = convertStreamToString(instream);
	            Log.i("Read from server", result);
	        }
	    } catch (Throwable t) {
	        Log.i("Request failed: ", t.toString());
	    }
	}

	/*
	* To convert the InputStream to String we use the BufferedReader.readLine()
	* method. We iterate until the BufferedReader return null which means
	* there's no more data to read. Each line will appended to a StringBuilder
	* and returned as String.
	*/
	private static String convertStreamToString(InputStream is) {
	        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
	        StringBuilder sb = new StringBuilder();
	 
	        String line = null;
	        try {
	            while ((line = reader.readLine()) != null) {
	                sb.append(line + "\n");
	        }
	    } catch (IOException e) {
	        e.printStackTrace();
	    } finally {
	        try {
	            is.close();
	        } catch (IOException e) {
	            e.printStackTrace();
	        }
	    }
	    return sb.toString();
	}
