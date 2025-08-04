# 🔄 Frontend Redeployment Guide - Environment Variable Fix

## 🎯 Current Situation
You have confirmed that `REACT_APP_API_URL=https://sunrise-school-backend-api.onrender.com/api/v1` is set in your Render frontend service environment variables.

However, our test showed that the frontend build doesn't contain this URL, which means:
1. The environment variable was added AFTER the last build
2. The frontend service needs to be redeployed to pick up the new environment variable

## 🚨 IMMEDIATE ACTION REQUIRED

### Step 1: Force Frontend Redeploy
Since React environment variables are **build-time variables**, you need to trigger a new build:

1. **Go to Render.com Dashboard**
2. **Click on your Frontend Service** (`sunrise-school-frontend-web`)
3. **Click "Manual Deploy" button**
4. **Select "Deploy latest commit"**
5. **Wait for the build to complete** (typically 5-10 minutes)

### Step 2: Monitor the Build Process
During the build, you should see in the build logs:
```
Building with environment variables:
REACT_APP_API_URL=https://sunrise-school-backend-api.onrender.com/api/v1
```

If you don't see this, the environment variable isn't being picked up.

### Step 3: Verify After Deployment
After the build completes:

1. **Clear your browser cache** (Ctrl+Shift+Delete)
2. **Visit your frontend**: `https://sunrise-school-frontend-web.onrender.com`
3. **Open Developer Tools** (F12)
4. **Go to Network tab**
5. **Login and navigate to Leave Management**
6. **Check API calls** - they should now go to `sunrise-school-backend-api.onrender.com`

## 🔍 Troubleshooting

### Issue 1: Build logs don't show REACT_APP_API_URL
**Cause:** Environment variable not properly set
**Solution:**
1. Double-check the environment variable name (must be exactly `REACT_APP_API_URL`)
2. Ensure there are no extra spaces
3. Save the environment variable and redeploy

### Issue 2: Still seeing localhost in API calls after redeploy
**Cause:** Browser cache or the environment variable still not in build
**Solution:**
1. Try incognito/private browsing mode
2. Hard refresh (Ctrl+F5)
3. Check Render build logs for environment variables

### Issue 3: Build fails during deployment
**Cause:** Possible build configuration issue
**Solution:**
1. Check build logs for specific errors
2. Ensure your `package.json` build script is correct
3. Verify no syntax errors in React code

## 🧪 Quick Test After Redeploy

Run this command to verify the fix worked:

```bash
python tests/backend/integration/test_leave_management_connection.py
```

You should now see:
```
✅ Frontend is accessible
✅ Backend URL found in frontend build
   Expected: https://sunrise-school-backend-api.onrender.com
```

## 📋 Expected Timeline

- **Build Start**: Immediate after clicking "Manual Deploy"
- **Build Duration**: 5-10 minutes
- **Cache Clear**: 1-2 minutes
- **Testing**: 2-3 minutes
- **Total Time**: ~10-15 minutes

## 🎉 Success Indicators

After successful redeploy, you should see:

1. **In Browser Network Tab:**
   - API calls to `sunrise-school-backend-api.onrender.com`
   - No calls to `localhost:8000`

2. **In Leave Management System:**
   - Data loads immediately
   - No "Backend server not running" error
   - All features work normally

3. **In Browser Console:**
   - No connection errors
   - Successful API responses

## 🚨 If Redeploy Doesn't Fix It

If the issue persists after redeployment:

### Check 1: Verify Environment Variable Format
Ensure it's exactly:
```
Key: REACT_APP_API_URL
Value: https://sunrise-school-backend-api.onrender.com/api/v1
```
(No trailing slash, no extra spaces)

### Check 2: Check Build Logs
Look for this in the Render build logs:
```
==> Building with environment variables
REACT_APP_API_URL=https://sunrise-school-backend-api.onrender.com/api/v1
```

### Check 3: Alternative Debugging
1. Add a temporary console.log in your React app:
   ```javascript
   console.log('API URL:', process.env.REACT_APP_API_URL);
   ```
2. Redeploy and check browser console

## 💡 Why This Happens

React environment variables starting with `REACT_APP_` are:
- **Build-time variables** (not runtime)
- **Baked into the JavaScript bundle** during build
- **Cannot be changed after build** without rebuilding

This is why adding the environment variable requires a redeploy to take effect.

---

**Next Step: Click "Manual Deploy" on your frontend service in Render.com now!**
