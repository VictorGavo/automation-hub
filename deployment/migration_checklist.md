# Raspberry Pi Migration Checklist
## Step-by-Step Migration from Cloudflare to Pi

**Pre-Migration Setup** ✅ = Complete | ⏳ = In Progress | ❌ = Not Started

---

## 📋 Phase 1: Preparation & Planning

### 1.1 Hardware & Domain Setup
- [ ] **Raspberry Pi 4B (4GB+)** - Obtained and powered on
- [ ] **MicroSD Card (32GB+)** - Flashed with Raspberry Pi OS Lite
- [ ] **Ethernet Connection** - Pi connected to router via ethernet
- [ ] **Domain Access** - DNS management access to your domain
- [ ] **Static IP** - Router configured to assign static IP to Pi (optional but recommended)

### 1.2 Current System Documentation
- [ ] **Cloudflare URLs** - Document current webhook URLs in Google Apps Script
- [ ] **Database Backup** - Create full backup of current PostgreSQL database
- [ ] **Configuration Export** - Save current config.py and environment variables
- [ ] **API Tokens** - Gather all Notion, Google Drive tokens for migration

### 1.3 Network Planning
- [ ] **Router Access** - Confirm ability to configure port forwarding
- [ ] **Public IP** - Document current public IP address
- [ ] **Firewall Rules** - Plan firewall configuration
- [ ] **DNS TTL** - Lower DNS TTL to 300 seconds for quick rollback

---

## 📋 Phase 2: Raspberry Pi Environment Setup

### 2.1 Operating System Configuration
```bash
# Commands to run on Pi
sudo apt update && sudo apt upgrade -y
```
- [ ] **System Updated** - All packages updated to latest versions
- [ ] **SSH Enabled** - SSH access configured and tested
- [ ] **User Setup** - Pi user has sudo privileges
- [ ] **Timezone Set** - Correct timezone configured

### 2.2 Automated Setup Script
```bash
# Run the setup script
chmod +x deployment/pi_setup.sh
./deployment/pi_setup.sh
```
- [ ] **Setup Script Run** - All packages installed successfully
- [ ] **PostgreSQL Running** - Database service active and configured
- [ ] **Nginx Installed** - Web server ready for configuration
- [ ] **Python Environment** - Virtual environment created with dependencies

### 2.3 Application Deployment
```bash
# Clone repository to Pi
git clone https://github.com/VictorGavo/automation-hub.git /opt/automation-hub
cd /opt/automation-hub
git checkout main
```
- [ ] **Code Deployed** - Latest stable code on Pi
- [ ] **Dependencies Installed** - All Python packages installed in venv
- [ ] **Environment File** - .env created and configured with production values
- [ ] **Permissions Set** - Correct file ownership and permissions

---

## 📋 Phase 3: Database Migration

### 3.1 Export Current Database
```bash
# On current system
pg_dump -h localhost -U admin automation_hub > automation_hub_migration.sql
```
- [ ] **Data Exported** - Complete database dump created
- [ ] **Backup Verified** - Dump file contains all expected tables and data
- [ ] **Transfer Ready** - Backup file copied to Pi or accessible location

### 3.2 Import to Pi Database
```bash
# On Pi
psql -h localhost -U automation_user -d automation_hub < automation_hub_migration.sql
```
- [ ] **Database Created** - Pi PostgreSQL database ready
- [ ] **Data Imported** - All tables and data successfully imported
- [ ] **Permissions Set** - Database user has correct privileges
- [ ] **Connection Tested** - Application can connect to database

---

## 📋 Phase 4: SSL & Domain Configuration

### 4.1 DNS Configuration
- [ ] **A Record Created** - Domain points to Pi's public IP
- [ ] **TTL Lowered** - DNS TTL set to 300 seconds for quick changes
- [ ] **Propagation Tested** - DNS changes visible globally
- [ ] **Backup DNS** - Document current DNS for rollback

### 4.2 SSL Certificate Setup
```bash
# On Pi - replace yourdomain.com with actual domain
sudo certbot --nginx -d yourdomain.com
```
- [ ] **Certificate Obtained** - Let's Encrypt SSL certificate issued
- [ ] **Nginx Updated** - SSL configuration automatically applied
- [ ] **Auto-Renewal** - Certbot renewal cron job configured
- [ ] **HTTPS Tested** - Domain accessible via HTTPS

### 4.3 Nginx Configuration
```bash
# Test nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```
- [ ] **Config Valid** - Nginx configuration syntax correct
- [ ] **Proxy Working** - Requests properly forwarded to Flask app
- [ ] **Rate Limiting** - Rate limits configured for webhook endpoints
- [ ] **Security Headers** - HTTPS security headers enabled

---

## 📋 Phase 5: Security & Monitoring

### 5.1 Firewall Configuration
```bash
sudo ufw status verbose
```
- [ ] **UFW Enabled** - Firewall active and configured
- [ ] **SSH Access** - SSH port properly secured
- [ ] **HTTP/HTTPS** - Web traffic allowed
- [ ] **Default Deny** - All other incoming traffic blocked

### 5.2 Intrusion Prevention
```bash
sudo systemctl status fail2ban
```
- [ ] **Fail2Ban Active** - Intrusion prevention running
- [ ] **SSH Protection** - SSH brute force protection enabled
- [ ] **Nginx Protection** - Rate limit violation protection configured
- [ ] **Log Monitoring** - Failed attempts being logged and blocked

### 5.3 Service Monitoring
```bash
sudo systemctl status automation-hub
```
- [ ] **Service Running** - Flask application service active
- [ ] **Auto-Start** - Service enabled for boot startup
- [ ] **Health Checks** - Automated health monitoring configured
- [ ] **Log Rotation** - Application logs rotating properly

---

## 📋 Phase 6: Pre-Migration Testing

### 6.1 Local Application Testing
```bash
# On Pi
cd /opt/automation-hub
python test_enhanced_processing.py
python test_full_integration.py
```
- [ ] **Enhanced Processing** - All SOD/EOD processing tests pass
- [ ] **Database Tests** - All database operations successful
- [ ] **Notion Integration** - API connections working (if enabled)
- [ ] **File Operations** - Google Drive sync working (if enabled)

### 6.2 External Access Testing
```bash
# From external system
curl -X GET https://yourdomain.com/health
```
- [ ] **HTTPS Access** - Domain accessible from internet
- [ ] **Health Endpoint** - Health check returns successful
- [ ] **SSL Certificate** - HTTPS certificate valid and secure
- [ ] **Rate Limiting** - Rate limits working as expected

### 6.3 Webhook Testing
```bash
# Test webhook endpoints
curl -X POST https://yourdomain.com/webhook/sod -H "Content-Type: application/json" -d '{"test": "data"}'
```
- [ ] **SOD Webhook** - Start-of-day endpoint responding
- [ ] **EOD Webhook** - End-of-day endpoint responding
- [ ] **Error Handling** - Proper error responses for malformed requests
- [ ] **Logging** - Webhook requests being logged correctly

---

## 📋 Phase 7: Migration Execution

### 7.1 Pre-Cutover
- [ ] **Final Backup** - Create final backup of current system
- [ ] **Maintenance Window** - Schedule migration during low-usage time
- [ ] **Team Notification** - Notify relevant people about migration
- [ ] **Rollback Plan** - Confirm rollback procedures are ready

### 7.2 DNS Cutover
```bash
# Update DNS A record
# yourdomain.com -> Pi_Public_IP (TTL: 300)
```
- [ ] **DNS Updated** - A record points to Pi IP address
- [ ] **Propagation Check** - DNS changes propagated globally
- [ ] **External Testing** - Domain resolves to Pi from multiple locations
- [ ] **Cache Clearing** - Local DNS caches cleared if needed

### 7.3 Google Apps Script Update
```javascript
// Update webhook URLs in Google Apps Script
const SOD_WEBHOOK = 'https://yourdomain.com/webhook/sod';
const EOD_WEBHOOK = 'https://yourdomain.com/webhook/eod';
```
- [ ] **SOD Form Updated** - Start-of-day form points to new URL
- [ ] **EOD Form Updated** - End-of-day form points to new URL  
- [ ] **Script Deployed** - Changes published and active
- [ ] **Test Submissions** - Test forms submit successfully

---

## 📋 Phase 8: Post-Migration Validation

### 8.1 Functionality Testing
- [ ] **SOD Form Test** - Submit actual SOD form and verify processing
- [ ] **EOD Form Test** - Submit actual EOD form and verify processing
- [ ] **Markdown Generation** - Daily templates generated correctly
- [ ] **Notion Updates** - Notion pages updated as expected (if enabled)

### 8.2 Performance Monitoring
```bash
# Monitor system resources
htop
df -h
sudo journalctl -u automation-hub -f
```
- [ ] **CPU Usage** - System running within acceptable limits
- [ ] **Memory Usage** - No memory leaks or excessive usage
- [ ] **Disk Space** - Adequate free space available
- [ ] **Network Traffic** - Normal traffic patterns observed

### 8.3 Log Analysis
```bash
# Check various logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u automation-hub -f
```
- [ ] **Access Logs** - Webhook requests being received and processed
- [ ] **Error Logs** - No unexpected errors or warnings
- [ ] **Application Logs** - SOD/EOD processing working correctly
- [ ] **Security Logs** - No suspicious activity detected

---

## 📋 Phase 9: Rollback Procedures (If Needed)

### 9.1 Quick Rollback
If issues are detected within first hour:
- [ ] **DNS Revert** - Change A record back to Cloudflare IP
- [ ] **Apps Script Revert** - Change webhook URLs back to Cloudflare
- [ ] **Service Check** - Verify old system still functioning

### 9.2 Data Sync Rollback
If migration was active for longer period:
- [ ] **Export Pi Data** - Backup any new data created on Pi
- [ ] **Merge Data** - Combine Pi data with original system
- [ ] **Verify Integrity** - Ensure no data loss occurred

---

## 📋 Phase 10: Post-Migration Optimization

### 10.1 Performance Tuning
```bash
# Database optimization
sudo -u postgres psql automation_hub -c "ANALYZE;"
```
- [ ] **Database Optimized** - Indexes and query performance reviewed
- [ ] **Nginx Tuning** - Connection limits and buffering optimized
- [ ] **Python Optimization** - Application performance monitored
- [ ] **Resource Monitoring** - Baseline performance metrics established

### 10.2 Backup & Maintenance
```bash
# Verify backup script
/opt/automation-hub/backup.sh
```
- [ ] **Automated Backups** - Daily backups running successfully
- [ ] **Backup Verification** - Backup integrity tested
- [ ] **Update Schedule** - Security update schedule established
- [ ] **Monitoring Setup** - Long-term monitoring and alerting configured

### 10.3 Documentation Update
- [ ] **Network Diagram** - Update infrastructure documentation
- [ ] **Runbook Updated** - Operational procedures documented
- [ ] **Contact Info** - Emergency contact information updated
- [ ] **Knowledge Transfer** - Team trained on new infrastructure

---

## 🚨 Emergency Contacts & Procedures

**If something goes wrong:**

1. **Immediate Issues (Service Down)**:
   - Check service status: `sudo systemctl status automation-hub`
   - Restart service: `sudo systemctl restart automation-hub`
   - Check logs: `sudo journalctl -u automation-hub -f`

2. **DNS/SSL Issues**:
   - Revert DNS to Cloudflare in domain provider
   - Check SSL certificate: `sudo certbot certificates`
   - Renew SSL: `sudo certbot renew`

3. **Database Issues**:
   - Check PostgreSQL: `sudo systemctl status postgresql`
   - Database connection: `psql -h localhost -U automation_user automation_hub`
   - Restore from backup: Follow backup restoration procedure

4. **Network/Security Issues**:
   - Check firewall: `sudo ufw status`
   - Check fail2ban: `sudo fail2ban-client status`
   - Review nginx logs: `sudo tail -f /var/log/nginx/error.log`

**Success Criteria**: 
✅ All checkboxes completed
✅ SOD/EOD forms working end-to-end  
✅ No errors in logs for 24 hours
✅ Performance within acceptable limits
✅ All team members trained on new system

---

*Migration completed on: ________________*  
*Completed by: ________________*  
*Post-migration review date: ________________*
