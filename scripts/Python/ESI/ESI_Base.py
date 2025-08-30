import hashlib
import json
import time
import requests
import email

class Base:

    defaultSuccessCodes = [200, 204]
    defaultCompatibilityDate = "2025-08-30"

    def hashRequest(self, url, method, payload, accessToken):
    
        hashingDict = {
            "URL": url, 
            "Method": method, 
            "Payload": payload, 
            "Authentication": accessToken
        }
        
        hashingData = str.encode(
            json.dumps(hashingDict, separators=(",", ":"))
        )
        
        return hashlib.sha256(hashingData).hexdigest()
        
    def cleanupCache(self):
    
        databaseCursor = self.databaseConnection.cursor(buffered=True)
    
        cleanupStatement = "DELETE FROM esicache WHERE expiration <= %s"
        currentTime = int(time.time())
        
        databaseCursor.execute(cleanupStatement, (currentTime,))
        
        self.databaseConnection.commit()
        databaseCursor.close()
        
    def checkCache(self, endpoint, hash):
    
        databaseCursor = self.databaseConnection.cursor(buffered=True)
    
        checkStatement = "SELECT response FROM esicache WHERE endpoint=%s AND hash=%s AND expiration > %s"
        currentTime = int(time.time())
        
        databaseCursor.execute(checkStatement, (endpoint, hash, currentTime))
        
        result = False
        
        for (response, ) in databaseCursor:
        
            result = json.loads(response)
        
        databaseCursor.close()
        
        return result
        
    def populateCache(self, endpoint, hash, response, expires):

        response_to_save = json.dumps(response, separators=(",", ":"))
    
        databaseCursor = self.databaseConnection.cursor(buffered=True)
    
        insertStatement = "INSERT INTO esicache (endpoint, hash, expiration, response) VALUES (%s, %s, %s, %s)"
        
        databaseCursor.execute(insertStatement, (endpoint, hash, expires, response_to_save))
        
        self.databaseConnection.commit()
        databaseCursor.close()
        
    def makeRequest(
        self, 
        endpoint, 
        url, 
        method = "GET", 
        payload = None, 
        accessToken = None, 
        compatibilityDate = None,
        expectResponse = True, 
        successCodes = [], 
        cacheTime = 0, 
        retries = 0
    ):
    
        responseData = {"Success": False, "Data": [], "Status Code": None, "Headers": None}
    
        self.cleanupCache()
        
        cacheCheck = self.checkCache(
            endpoint,
            self.hashRequest(url, method, payload, accessToken)
        )
        
        if cacheCheck != False:
        
            responseData = cacheCheck
            
            return responseData
            
        else:
        
            for retryCounter in range(retries + 1):
            
                requestMethod = getattr(requests, method.lower())
                
                headers = {
                    "accept": "application/json",
                    "X-Compatibility-Date": (compatibilityDate if compatibilityDate is not None else self.defaultCompatibilityDate)
                }
                
                if accessToken is not None:
                
                    headers["Authorization"] = "Bearer " + accessToken
                    
                if payload is not None:
                
                    requestData = json.dumps(payload)
                    headers["Content-Type"] = "application/json"
                    
                else:
                
                    requestData = None
                
                request = requestMethod(
                    url = url, 
                    data = requestData, 
                    headers = headers
                )

                responseData["Status Code"] = request.status_code
                responseData["Headers"] = dict(request.headers)
                
                if request.status_code in (self.defaultSuccessCodes + successCodes):
                
                    responseData["Success"] = True
                    
                    if expectResponse:
                    
                        try:
                            responseData["Data"] = json.loads(request.text)
                        except:
                            pass
                        
                        if "Expires" in request.headers:
                        
                            expiryDatetime = email.utils.parsedate_to_datetime(request.headers["Expires"])
                            expiry = int(expiryDatetime.timestamp())
                        
                        else:
                        
                            expiry = int(time.time()) + cacheTime
                        
                        self.populateCache(
                            endpoint, 
                            self.hashRequest(url, method, payload, accessToken), 
                            responseData, 
                            expiry
                        )
                        
                    return responseData
                    
                elif retryCounter == retries:
                
                    responseData["Success"] = False
                    
                    if expectResponse:
                    
                        try:
                        
                            responseData["Data"] = json.loads(request.text)
                        
                        except:
                        
                            pass
                        
                    return responseData
            