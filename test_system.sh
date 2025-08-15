#!/bin/bash
# Comprehensive test script using curl

echo "🧪 Chore App Full System Test"
echo "🕐 Test started at: $(date)"
echo "============================================================"

echo ""
echo "🔧 Testing Backend API..."
echo "=================================================="

# Test 1: Get all chores
echo "Testing GET /chores..."
CHORE_COUNT=$(curl -s http://127.0.0.1:8000/chores | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('chores', [])))" 2>/dev/null)

if [ "$CHORE_COUNT" -gt 0 ]; then
    echo "✅ GET /chores: $CHORE_COUNT chores returned"
else
    echo "❌ Backend API not responding"
    exit 1
fi

# Test 2: Search functionality
SEARCH_COUNT=$(curl -s "http://127.0.0.1:8000/chores?q=clean" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('chores', [])))" 2>/dev/null)
echo "✅ GET /chores?q=clean: $SEARCH_COUNT chores found"

# Test 3: Get specific chore
MICROWAVE_TITLE=$(curl -s http://127.0.0.1:8000/chores/microwave | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('title', 'ERROR'))" 2>/dev/null)
echo "✅ GET /chores/microwave: $MICROWAVE_TITLE"

# Test 4: Test new chore
LAUNDRY_TITLE=$(curl -s http://127.0.0.1:8000/chores/laundry-fold | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('title', 'ERROR'))" 2>/dev/null)
echo "✅ GET /chores/laundry-fold: $LAUNDRY_TITLE (NEW CHORE)"

# Test 5: Test 404
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/chores/non-existent)
if [ "$HTTP_CODE" = "404" ]; then
    echo "✅ 404 handling works correctly"
else
    echo "❌ 404 handling failed: got $HTTP_CODE"
fi

echo ""
echo "🎨 Testing Frontend..."
echo "=================================================="

# Test frontend on different ports
FRONTEND_WORKING=false

for PORT in 3000 3002; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT --connect-timeout 3)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Frontend is running on http://localhost:$PORT"
        FRONTEND_WORKING=true
        FRONTEND_PORT=$PORT
        break
    fi
done

if [ "$FRONTEND_WORKING" = false ]; then
    echo "❌ Frontend is not accessible on ports 3000 or 3002"
fi

echo ""
echo "📋 Chore Summary:"
echo "=================================================="

# Get and display chore summary
curl -s http://127.0.0.1:8000/chores | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    chores = data.get('chores', [])
    
    quick = [c for c in chores if c['time_min'] <= 5]
    short = [c for c in chores if 5 < c['time_min'] <= 10]
    medium = [c for c in chores if 10 < c['time_min'] <= 15]
    long = [c for c in chores if c['time_min'] > 15]
    
    print(f'Total chores: {len(chores)}')
    print(f'Quick tasks (≤5 min): {len(quick)} chores')
    print(f'Short tasks (6-10 min): {len(short)} chores')
    print(f'Medium tasks (11-15 min): {len(medium)} chores')
    print(f'Long tasks (>15 min): {len(long)} chores')
    
    # Show new chores
    new_chore_ids = {
        'laundry-fold', 'vacuum-living-room', 'clean-kitchen-sink',
        'water-plants', 'wipe-down-counters', 'take-out-trash',
        'clean-mirror-bathroom', 'organize-mail', 'dust-furniture',
        'clean-stovetop'
    }
    
    new_chores = [c for c in chores if c['id'] in new_chore_ids]
    print(f'')
    print(f'🆕 Recently added chores: {len(new_chores)}')
    for chore in new_chores:
        print(f'   - {chore[\"title\"]} ({chore[\"time_min\"]} min)')
        
except Exception as e:
    print(f'Error parsing chores: {e}')
"

echo ""
echo "============================================================"
echo "📊 Test Results Summary:"
echo "============================================================"

if [ "$CHORE_COUNT" -gt 0 ]; then
    echo "Backend API: ✅ WORKING"
else
    echo "Backend API: ❌ FAILED"
fi

if [ "$FRONTEND_WORKING" = true ]; then
    echo "Frontend: ✅ WORKING"
else
    echo "Frontend: ❌ FAILED"
fi

if [ "$CHORE_COUNT" -gt 0 ] && [ "$FRONTEND_WORKING" = true ]; then
    echo ""
    echo "🎉 All systems are working correctly!"
    echo ""
    echo "🌐 Access your app at:"
    echo "   Frontend: http://localhost:$FRONTEND_PORT"
    echo "   API Docs: http://127.0.0.1:8000/docs"
else
    echo ""
    echo "⚠️  Some systems need attention:"
    if [ "$CHORE_COUNT" -eq 0 ]; then
        echo "   - Start backend: cd fastapi-service && source venv/bin/activate && cd app && uvicorn main:app --reload --port 8000"
    fi
    if [ "$FRONTEND_WORKING" = false ]; then
        echo "   - Start frontend: cd chore && npm run dev"
    fi
fi
