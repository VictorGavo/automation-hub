#!/bin/bash
# SSL Certificate Setup Script for Automation Hub
# Run this AFTER DNS is pointing to your Pi

set -e

# Configuration
DOMAIN=""
EMAIL=""
NGINX_CONFIG="/etc/nginx/sites-available/automation-hub"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

show_usage() {
    echo "Usage: $0 -d DOMAIN -e EMAIL"
    echo ""
    echo "Options:"
    echo "  -d DOMAIN    Your domain name (e.g., example.com)"
    echo "  -e EMAIL     Your email address for Let's Encrypt"
    echo "  -h           Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -d example.com -e admin@example.com"
}

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if running as non-root user
    if [ "$EUID" -eq 0 ]; then
        print_error "Don't run this script as root"
        exit 1
    fi
    
    # Check if nginx is installed and running
    if ! systemctl is-active --quiet nginx; then
        print_error "Nginx is not running. Please start nginx first."
        exit 1
    fi
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        print_error "Certbot is not installed. Please install it first."
        exit 1
    fi
    
    # Check if domain is provided
    if [ -z "$DOMAIN" ]; then
        print_error "Domain is required. Use -d flag."
        show_usage
        exit 1
    fi
    
    # Check if email is provided
    if [ -z "$EMAIL" ]; then
        print_error "Email is required. Use -e flag."
        show_usage
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

check_dns_propagation() {
    print_status "Checking DNS propagation for $DOMAIN..."
    
    # Get Pi's public IP
    PI_IP=$(curl -s https://ipinfo.io/ip || curl -s https://api.ipify.org)
    
    if [ -z "$PI_IP" ]; then
        print_error "Could not determine Pi's public IP address"
        exit 1
    fi
    
    print_status "Pi's public IP: $PI_IP"
    
    # Check DNS resolution
    RESOLVED_IP=$(dig +short "$DOMAIN" @8.8.8.8 | tail -n1)
    
    if [ -z "$RESOLVED_IP" ]; then
        print_error "Domain $DOMAIN does not resolve to any IP address"
        print_error "Please ensure DNS A record is configured correctly"
        exit 1
    fi
    
    print_status "Domain resolves to: $RESOLVED_IP"
    
    if [ "$PI_IP" != "$RESOLVED_IP" ]; then
        print_warning "DNS mismatch detected!"
        print_warning "Pi IP: $PI_IP"
        print_warning "DNS IP: $RESOLVED_IP"
        echo ""
        print_warning "This might cause certificate issuance to fail."
        echo -n "Continue anyway? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_status "Exiting. Please fix DNS configuration first."
            exit 1
        fi
    else
        print_status "DNS configuration looks correct!"
    fi
}

update_nginx_config() {
    print_status "Updating Nginx configuration with domain name..."
    
    # Create backup of current config
    sudo cp "$NGINX_CONFIG" "$NGINX_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Replace placeholder domain with actual domain
    sudo sed -i "s/server_name _;/server_name $DOMAIN;/g" "$NGINX_CONFIG"
    
    # Test nginx configuration
    if sudo nginx -t; then
        print_status "Nginx configuration updated successfully"
        sudo systemctl reload nginx
    else
        print_error "Nginx configuration test failed!"
        # Restore backup
        sudo cp "$NGINX_CONFIG.backup.$(date +%Y%m%d_%H%M%S)" "$NGINX_CONFIG"
        exit 1
    fi
}

test_http_access() {
    print_status "Testing HTTP access to $DOMAIN..."
    
    # Test if we can reach the domain on port 80
    if curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/health" | grep -q "200\|404\|502"; then
        print_status "HTTP access working - ready for SSL certificate"
    else
        print_error "Cannot reach $DOMAIN on HTTP"
        print_error "Please check:"
        print_error "  1. DNS propagation (may take up to 48 hours)"
        print_error "  2. Port forwarding (port 80 -> Pi IP:80)"
        print_error "  3. Firewall settings"
        exit 1
    fi
}

obtain_ssl_certificate() {
    print_status "Obtaining SSL certificate from Let's Encrypt..."
    
    # Use certbot with nginx plugin
    sudo certbot --nginx \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        --redirect
    
    if [ $? -eq 0 ]; then
        print_status "SSL certificate obtained successfully!"
    else
        print_error "Failed to obtain SSL certificate"
        print_error "Common issues:"
        print_error "  1. DNS not propagated yet"
        print_error "  2. Port 80 not accessible from internet"
        print_error "  3. Rate limiting (if you've tried multiple times)"
        exit 1
    fi
}

setup_auto_renewal() {
    print_status "Setting up automatic certificate renewal..."
    
    # Test renewal process
    sudo certbot renew --dry-run
    
    if [ $? -eq 0 ]; then
        print_status "Certificate auto-renewal test successful"
        
        # Add renewal check to crontab if not already present
        if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
            (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
            print_status "Added certificate renewal to crontab"
        else
            print_status "Certificate renewal already configured in crontab"
        fi
    else
        print_warning "Certificate renewal test failed"
        print_warning "Manual renewal may be required"
    fi
}

test_ssl_configuration() {
    print_status "Testing SSL configuration..."
    
    # Wait a moment for nginx to reload
    sleep 2
    
    # Test HTTPS access
    if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/health" | grep -q "200\|404\|502"; then
        print_status "HTTPS access working!"
        
        # Test SSL certificate
        SSL_INFO=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN":443 2>/dev/null | openssl x509 -noout -dates)
        print_status "Certificate info:"
        echo "$SSL_INFO"
        
        # Test HTTP to HTTPS redirect
        REDIRECT_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/health")
        if [ "$REDIRECT_CODE" = "301" ] || [ "$REDIRECT_CODE" = "302" ]; then
            print_status "HTTP to HTTPS redirect working correctly"
        else
            print_warning "HTTP to HTTPS redirect may not be working (got code: $REDIRECT_CODE)"
        fi
        
    else
        print_error "HTTPS access failed"
        exit 1
    fi
}

check_security_headers() {
    print_status "Checking security headers..."
    
    HEADERS=$(curl -s -I "https://$DOMAIN/health")
    
    if echo "$HEADERS" | grep -q "Strict-Transport-Security"; then
        print_status "✓ HSTS header present"
    else
        print_warning "✗ HSTS header missing"
    fi
    
    if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
        print_status "✓ Content-Type-Options header present"
    else
        print_warning "✗ Content-Type-Options header missing"
    fi
    
    if echo "$HEADERS" | grep -q "X-Frame-Options"; then
        print_status "✓ X-Frame-Options header present"
    else
        print_warning "✗ X-Frame-Options header missing"
    fi
}

print_completion_summary() {
    print_header ""
    print_header "🎉 SSL Setup Complete!"
    print_header "======================"
    print_header ""
    print_status "Your domain $DOMAIN is now secured with SSL!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Update Google Apps Script webhook URLs to:"
    print_status "   SOD: https://$DOMAIN/webhook/sod"
    print_status "   EOD: https://$DOMAIN/webhook/eod"
    print_status ""
    print_status "2. Test your webhooks:"
    print_status "   curl -X POST https://$DOMAIN/webhook/sod -H 'Content-Type: application/json' -d '{\"test\": \"data\"}'"
    print_status ""
    print_status "3. Monitor your logs:"
    print_status "   sudo tail -f /var/log/nginx/access.log"
    print_status "   sudo journalctl -u automation-hub -f"
    print_status ""
    print_status "Certificate info:"
    print_status "- Certificate will auto-renew via cron job"
    print_status "- Renewal runs daily at 12:00 PM"
    print_status "- Check renewal status: sudo certbot certificates"
    print_status ""
    print_warning "Security checklist:"
    print_warning "- Update Google Apps Script URLs"
    print_warning "- Test form submissions end-to-end"
    print_warning "- Monitor logs for any issues"
    print_warning "- Verify certificate renewal in 60 days"
}

# Parse command line arguments
while getopts "d:e:h" opt; do
    case $opt in
        d)
            DOMAIN="$OPTARG"
            ;;
        e)
            EMAIL="$OPTARG"
            ;;
        h)
            show_usage
            exit 0
            ;;
        \?)
            print_error "Invalid option: -$OPTARG"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header "🔒 Automation Hub SSL Setup"
    print_header "============================="
    
    check_prerequisites
    check_dns_propagation
    update_nginx_config
    test_http_access
    obtain_ssl_certificate
    setup_auto_renewal
    test_ssl_configuration
    check_security_headers
    print_completion_summary
}

# Run main function
main "$@"
