# Custom Domain Configuration Guide for Render Deployment

## Overview
This guide documents the complete process of configuring a custom domain (sunrisenps.com) for a web application deployed on Render.com, including common issues and solutions encountered during setup.

**Application:** Sunrise School Management System  
**Domain Registrar:** GoDaddy  
**Hosting Platform:** Render.com  
**Frontend Service:** sunrise-school-frontend-web  
**Backend Service:** sunrise-backend-fastapi  

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Configure DNS in GoDaddy](#step-1-configure-dns-in-godaddy)
3. [Step 2: Add Custom Domain in Render](#step-2-add-custom-domain-in-render)
4. [Step 3: Configure Backend CORS](#step-3-configure-backend-cors)
5. [Common Issues and Solutions](#common-issues-and-solutions)
6. [Verification and Testing](#verification-and-testing)
7. [Troubleshooting Commands](#troubleshooting-commands)

---

## Prerequisites

- ✅ Domain purchased from GoDaddy (or any registrar)
- ✅ Application deployed on Render.com
- ✅ Access to domain registrar DNS settings
- ✅ Access to Render dashboard

---

## Step 1: Configure DNS in GoDaddy

### 1.1 Access DNS Management

1. Login to **GoDaddy**
2. Go to **My Products → Domains**
3. Click on your domain (e.g., `sunrisenps.com`)
4. Click **DNS** button

### 1.2 Delete Conflicting Records

**⚠️ CRITICAL:** Remove any existing conflicting records:

- ❌ Delete "WebsiteBuilder Site" A record
- ❌ Delete any other A records pointing to GoDaddy IPs
- ❌ Delete CNAME for @ (root domain) if exists
- ❌ Delete any parking page records

**Why?** These records will conflict with Render's configuration and cause your domain to show GoDaddy content instead of your application.

### 1.3 Add Required DNS Records

Add the following two records:

#### A Record (Root Domain)
| Field | Value |
|-------|-------|
| Type | A |
| Name | @ |
| Value | 216.24.57.1 |
| TTL | 600 seconds (or default) |

**Purpose:** Points root domain (sunrisenps.com) to Render's IP address.

#### CNAME Record (WWW Subdomain)
| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | www |
| Value | sunrise-school-frontend-web.onrender.com |
| TTL | 600 seconds (or default) |

**Purpose:** Points www subdomain (www.sunrisenps.com) to your Render service.

### 1.4 Save Changes

Click **Save** and wait for changes to propagate.

**⏰ DNS Propagation Time:** 15 minutes to 48 hours (typically 30-60 minutes)

---

## Step 2: Add Custom Domain in Render

### 2.1 Access Render Dashboard

1. Login to **Render.com**
2. Navigate to your **Frontend service** (sunrise-school-frontend-web)
3. Go to **Settings** tab
4. Scroll to **Custom Domains** section

### 2.2 Add Root Domain

1. Click **Add Custom Domain**
2. Enter: `sunrisenps.com`
3. Click **Save**

**Expected Status:**
- ⏳ Initially: "Verifying..."
- ✅ After DNS propagates: "Domain Verified"
- ✅ SSL Certificate: "Certificate Issued" (automatic)

### 2.3 Add WWW Subdomain

1. Click **Add Custom Domain** again
2. Enter: `www.sunrisenps.com`
3. Click **Save**
4. Configure redirect to root domain (optional but recommended)

**Expected Status:**
- ✅ Domain Verified
- ✅ Certificate Issued
- ✅ Redirects to sunrisenps.com

### 2.4 Wait for Verification

**Render will automatically:**
- ✅ Verify domain ownership via DNS
- ✅ Issue SSL certificate (Let's Encrypt)
- ✅ Enable HTTPS
- ✅ Configure automatic HTTP → HTTPS redirect

**Time Required:** 5-15 minutes after DNS propagates

---

## Step 3: Configure Backend CORS

### 3.1 Why CORS Configuration is Required

When your frontend domain changes from `.onrender.com` to your custom domain, the backend must allow requests from the new domain to prevent CORS (Cross-Origin Resource Sharing) errors.

### 3.2 Update Backend Environment Variables

1. Go to **Render Dashboard**
2. Navigate to your **Backend service** (sunrise-backend-fastapi)
3. Click **Environment** tab
4. Find or add: `BACKEND_CORS_ORIGINS`

### 3.3 Set CORS Origins

**Add/Update the following value:**

```
https://sunrise-school-frontend-web.onrender.com,https://sunrisenps.com,https://www.sunrisenps.com
```

**⚠️ Important Notes:**
- ✅ Use HTTPS (not HTTP)
- ✅ Separate multiple origins with commas (no spaces)
- ✅ Include both root and www domains
- ✅ Keep original .onrender.com URL for backup access
- ❌ Do NOT include localhost URLs in production (handled by code)

### 3.4 Save and Redeploy

1. Click **Save Changes**
2. Backend will automatically redeploy (2-3 minutes)
3. Wait for "Deploy live" status

**⚠️ Critical:** Frontend will not work properly until backend CORS is updated!

---

## Common Issues and Solutions

### Issue 1: "The connection for this site is not secure" (ERR_SSL_VERSION_OR_CIPHER_MISMATCH)

**Symptom:** Browser shows SSL error when accessing `http://sunrisenps.com`

**Cause:** Accessing site via HTTP instead of HTTPS

**Solution:**
- ✅ Always use `https://sunrisenps.com` (not `http://`)
- ✅ Render only serves HTTPS for security
- ✅ Bookmark the HTTPS version
- ✅ Share HTTPS links only

**Prevention:** Always include `https://` when sharing your domain URL.

---

### Issue 2: Domain Shows GoDaddy Parking Page or Website Builder Content

**Symptom:** Visiting domain shows GoDaddy content instead of your application

**Causes:**
1. DNS hasn't propagated yet
2. "WebsiteBuilder Site" A record still exists
3. Local DNS/browser cache showing old content

**Solutions:**

#### Solution A: Delete Conflicting DNS Records
1. Go to GoDaddy DNS Management
2. Delete "WebsiteBuilder Site" A record
3. Delete any other conflicting A records
4. Wait 30-60 minutes for propagation

#### Solution B: Clear Local DNS Cache (Windows)

Open **Command Prompt as Administrator** and run:

```bash
ipconfig /flushdns
ipconfig /registerdns
ipconfig /release
ipconfig /renew
```

#### Solution C: Clear Browser Cache

1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files" and "Cookies"
3. Time range: "All time"
4. Click "Clear data"
5. Close ALL browser windows
6. Open fresh browser window

#### Solution D: Change DNS to Google DNS

**Temporary fix to bypass ISP DNS cache:**

1. Press `Windows Key + R`
2. Type `ncpa.cpl` and press Enter
3. Right-click network connection → Properties
4. Select "Internet Protocol Version 4 (TCP/IPv4)" → Properties
5. Select "Use the following DNS server addresses"
6. Enter:
   - Preferred: `8.8.8.8`
   - Alternate: `8.8.4.4`
7. Click OK
8. Run `ipconfig /flushdns`
9. Try accessing site again

#### Solution E: Test on Mobile Data

**Quick verification that DNS is working globally:**

1. Use smartphone
2. Disconnect from WiFi (use mobile data)
3. Visit `https://sunrisenps.com`
4. Should load your application (not GoDaddy content)

**If it works on mobile:** Issue is local DNS cache, wait or clear cache

---

### Issue 3: CORS Errors After Domain Change

**Symptom:** Browser console shows errors like:
```
Access to XMLHttpRequest at 'https://[backend].onrender.com/api/v1/...' 
from origin 'https://sunrisenps.com' has been blocked by CORS policy
```

**Cause:** Backend CORS not configured for new custom domain

**Solution:**
1. Update backend `BACKEND_CORS_ORIGINS` environment variable
2. Include custom domain in CORS origins
3. Wait for backend to redeploy (2-3 minutes)
4. Clear browser cache
5. Try again

**Verification:**
- ✅ Login should work without errors
- ✅ API calls should succeed (check Network tab)
- ✅ No CORS errors in browser console

---

### Issue 4: Domain Verified but SSL Certificate Not Issued

**Symptom:** Render shows "Domain Verified" but no SSL certificate

**Causes:**
1. DNS not fully propagated
2. CAA records blocking Let's Encrypt
3. Render SSL provisioning delay

**Solutions:**
1. Wait 15-30 minutes for automatic retry
2. Check for CAA DNS records that might block Let's Encrypt
3. Contact Render support if issue persists beyond 1 hour

---

### Issue 5: WWW Subdomain Not Redirecting

**Symptom:** `www.sunrisenps.com` doesn't redirect to `sunrisenps.com`

**Solution:**
1. Ensure CNAME record exists for www
2. In Render, both domains should be added separately
3. Render automatically handles www → root redirect
4. Clear DNS cache and test again

---

## Verification and Testing

### Step 1: Check DNS Propagation

**Use online tool:**
1. Visit: https://dnschecker.org/
2. Enter: `sunrisenps.com`
3. Select: A record
4. Verify: Shows `216.24.57.1` globally (green checkmarks)

**Expected Result:** All or most locations show correct IP address

### Step 2: Test Domain Access

**Test these URLs:**

| URL | Expected Result |
|-----|-----------------|
| `https://sunrisenps.com` | ✅ Loads application with SSL |
| `https://www.sunrisenps.com` | ✅ Redirects to https://sunrisenps.com |
| `http://sunrisenps.com` | ⚠️ May show SSL error (by design) |

**Verification:**
- ✅ Green padlock 🔒 in address bar
- ✅ Certificate valid (click padlock to verify)
- ✅ Application loads correctly

### Step 3: Test Login and API Communication

1. Visit `https://sunrisenps.com`
2. Open browser console (F12 → Console tab)
3. Login with credentials:
   - Email: `admin@sunrise.com`
   - Password: `admin123`
4. Check console for errors

**Expected Results:**
- ✅ Login succeeds
- ✅ No CORS errors in console
- ✅ API calls show status 200 in Network tab
- ✅ Dashboard loads with data

### Step 4: Test All Features

Verify all application features work:
- [ ] Fee Management
- [ ] Student Management
- [ ] Teacher Management
- [ ] Leave Management
- [ ] Expense Management
- [ ] Reports and Statistics

---

## Troubleshooting Commands

### Check DNS Resolution

```bash
# Check DNS using system resolver
nslookup sunrisenps.com

# Check DNS using Google DNS
nslookup sunrisenps.com 8.8.8.8

# Check DNS using Cloudflare DNS
nslookup sunrisenps.com 1.1.1.1
```

**Expected Output:**
```
Name:    sunrisenps.com
Address: 216.24.57.1
```

### Clear DNS Cache (Windows)

```bash
# Flush DNS resolver cache
ipconfig /flushdns

# Re-register DNS
ipconfig /registerdns

# Release and renew IP
ipconfig /release
ipconfig /renew
```

### Test SSL Certificate

```bash
# Using OpenSSL (if installed)
openssl s_client -connect sunrisenps.com:443 -servername sunrisenps.com
```

### Check HTTP Headers

```bash
# Using curl (if installed)
curl -I https://sunrisenps.com
```

---

## Best Practices

### 1. Always Use HTTPS
- ✅ Share links as `https://sunrisenps.com`
- ✅ Update bookmarks to HTTPS version
- ✅ Update documentation with HTTPS URLs

### 2. Monitor DNS Propagation
- Use https://dnschecker.org/ to verify global propagation
- Wait for green checkmarks in multiple locations
- Don't panic if it takes 1-2 hours

### 3. Keep Backup Access
- Keep original `.onrender.com` URL in CORS origins
- Provides backup access if custom domain has issues
- Useful for debugging

### 4. Document Configuration
- Save DNS record values
- Document environment variables
- Keep this guide updated with any changes

### 5. Test Thoroughly
- Test on multiple browsers
- Test on mobile devices
- Test all application features
- Verify SSL certificate validity

---

## Configuration Summary

### Final DNS Configuration (GoDaddy)
| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 216.24.57.1 | 600 |
| CNAME | www | sunrise-school-frontend-web.onrender.com | 600 |

### Final Render Configuration
| Domain | Status | SSL | Redirect |
|--------|--------|-----|----------|
| sunrisenps.com | ✅ Verified | ✅ Issued | - |
| www.sunrisenps.com | ✅ Verified | ✅ Issued | → sunrisenps.com |

### Final Backend Configuration
| Variable | Value |
|----------|-------|
| BACKEND_CORS_ORIGINS | https://sunrise-school-frontend-web.onrender.com,https://sunrisenps.com,https://www.sunrisenps.com |

---

## Timeline Reference

Based on actual deployment experience:

| Task | Time Required |
|------|---------------|
| Configure DNS in GoDaddy | 5-10 minutes |
| Add custom domain in Render | 2-3 minutes |
| DNS propagation | 30-60 minutes (can be up to 48 hours) |
| SSL certificate issuance | 5-15 minutes (automatic) |
| Backend CORS update | 2-3 minutes (redeploy time) |
| Local DNS cache clear | Immediate |
| **Total Time** | **1-2 hours typically** |

---

## Support Resources

### DNS Propagation Checker
- https://dnschecker.org/

### Render Documentation
- https://render.com/docs/custom-domains

### GoDaddy DNS Help
- https://www.godaddy.com/help/manage-dns-records-680

### SSL Certificate Checker
- https://www.sslshopper.com/ssl-checker.html

---

## Conclusion

Custom domain configuration involves three main components:
1. **DNS Configuration** (GoDaddy) - Points domain to Render
2. **Domain Verification** (Render) - Verifies ownership and issues SSL
3. **CORS Configuration** (Backend) - Allows API communication

**Key Success Factors:**
- ✅ Delete conflicting DNS records
- ✅ Wait for DNS propagation
- ✅ Clear local caches
- ✅ Update backend CORS
- ✅ Always use HTTPS

**Common Pitfalls:**
- ❌ Forgetting to delete "WebsiteBuilder Site" record
- ❌ Accessing via HTTP instead of HTTPS
- ❌ Not clearing local DNS cache
- ❌ Forgetting to update backend CORS
- ❌ Not waiting long enough for DNS propagation

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-11  
**Application:** Sunrise School Management System  
**Domain:** sunrisenps.com  
**Platform:** Render.com

