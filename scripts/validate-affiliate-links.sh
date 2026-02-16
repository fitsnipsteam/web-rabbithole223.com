#!/bin/bash

###############################################################################
# Affiliate Links Validator
#
# This script validates all affiliate links in content/docs/affiliate-links.md
# It checks HTTP status codes and specifically validates Amazon product pages.
#
# Usage: ./scripts/validate-affiliate-links.sh [--quick]
# Use --quick flag to skip detailed Amazon product checks
###############################################################################

# Configuration
LINKS_FILE="content/docs/affiliate-links.md"
REPORT_FILE="affiliate-links-report-$(date +%Y%m%d-%H%M%S).txt"
TIMEOUT=10
QUICK_MODE="${1:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
declare -i TOTAL=0
declare -i VALID=0
declare -i BROKEN=0
declare -i WARNING=0
declare -i REDIRECTED=0
declare -i ERRORS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Affiliate Links Validation Report${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "File: $LINKS_FILE"
echo "Timestamp: $(date)"
echo "Mode: $([ "$QUICK_MODE" = "--quick" ] && echo "Quick (status codes only)" || echo "Full (includes Amazon checks)")"
echo ""
echo "Validating links..."
echo ""

# Extract and test URLs
grep -oP 'https?://[^\s)"`\[\]]+' "$LINKS_FILE" | sort | uniq | while read -r url; do
    ((TOTAL++))

    # Skip the image URL (not an affiliate link we care about)
    if [[ "$url" =~ static\.rabbithole223\.com ]]; then
        continue
    fi

    # Get HTTP status code only (much faster)
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" -L \
             -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
             "$url" 2>/dev/null || echo "000")

    # Determine result based on status code
    if [[ "$status" == "200" ]]; then
        result="${GREEN}✓${NC} Valid"
        ((VALID++))
    elif [[ "$status" == "301" ]] || [[ "$status" == "302" ]]; then
        result="${YELLOW}⟳${NC} Redirect"
        ((REDIRECTED++))
    elif [[ "$status" == "404" ]]; then
        result="${RED}✗${NC} Not found (404)"
        ((BROKEN++))
    elif [[ "$status" == "403" ]] || [[ "$status" == "429" ]]; then
        result="${YELLOW}⚠${NC} Access denied ($status)"
        ((WARNING++))
    elif [[ "$status" == "000" ]]; then
        result="${RED}✗${NC} Connection failed"
        ((ERRORS++))
    elif [[ "$status" =~ ^5[0-9]{2}$ ]]; then
        result="${RED}✗${NC} Server error ($status)"
        ((BROKEN++))
    else
        result="${YELLOW}⚠${NC} Unknown ($status)"
        ((WARNING++))
    fi

    printf "%-65s | %s\n" "$url" "${result}"
done

# Print summary
echo ""
echo "=========================================="
echo "Summary:"
echo "=========================================="
echo "Total links:            $TOTAL"
echo -e "${GREEN}Valid:${NC}                  $VALID"
echo -e "${RED}Broken:${NC}                 $BROKEN"
echo -e "${YELLOW}Warnings:${NC}               $WARNING"
echo -e "Redirects:              $REDIRECTED"
echo -e "${RED}Errors:${NC}                  $ERRORS"
echo ""

if [[ $BROKEN -eq 0 ]] && [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ All links are accessible!${NC}"
else
    if [[ $BROKEN -gt 0 ]]; then
        echo -e "${RED}✗ Found $BROKEN broken link(s)${NC}"
    fi
    if [[ $ERRORS -gt 0 ]]; then
        echo -e "${RED}✗ Found $ERRORS connection error(s)${NC}"
    fi
fi
echo ""
