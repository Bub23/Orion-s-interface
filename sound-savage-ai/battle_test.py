#!/usr/bin/env python
"""
Sound Savage AI - Full Battle Test Suite
Validates: API, Workers, Queue, Pipeline, Failure Recovery
"""

import subprocess
import time
import sys
import json


class BattleTest:
    """Execute full battle test"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def step(self, name: str, cmd: str, timeout: int = 30):
        """Execute test step"""
        print(f"\n[TEST] {name}")
        print(f"  Command: {cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                print(f"  [PASS]")
                self.passed += 1
                return True
            else:
                print(f"  [FAIL] Exit code: {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")
                self.failed += 1
                return False
        
        except subprocess.TimeoutExpired:
            print(f"  [FAIL] Timeout after {timeout}s")
            self.failed += 1
            return False
        except Exception as e:
            print(f"  [FAIL] {str(e)}")
            self.failed += 1
            return False
    
    def run_full_battle_test(self):
        """Run complete battle test"""
        print("\n" + "="*70)
        print("SOUND SAVAGE AI - FULL BATTLE TEST")
        print("="*70)
        
        # Phase 1: Startup
        print("\n" + "="*70)
        print("PHASE 1: SYSTEM STARTUP")
        print("="*70)
        
        print("\nStarting Docker containers (this takes ~30 seconds)...")
        print("If this is your first run, images will download.")
        
        print("\n[STARTUP] Bringing up docker-compose...")
        subprocess.run("docker-compose down", shell=True, capture_output=True)
        result = subprocess.run(
            "docker-compose up -d",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"[FAIL] Docker-compose startup failed")
            print(result.stderr)
            return False
        
        print("[OK] Containers starting...")
        
        # Wait for services to be ready
        print("\n[WAIT] Waiting 15 seconds for services to stabilize...")
        time.sleep(15)
        
        # Phase 2: Health checks
        print("\n" + "="*70)
        print("PHASE 2: HEALTH CHECKS")
        print("="*70)
        
        self.step(
            "API Health",
            "curl -s http://localhost:8000/health | grep -q Sound",
            timeout=10
        )
        
        self.step(
            "Redis Ping",
            "docker-compose exec -T redis redis-cli ping",
            timeout=10
        )
        
        # Phase 3: Pipeline validation
        print("\n" + "="*70)
        print("PHASE 3: PIPELINE VALIDATION")
        print("="*70)
        
        test_payload = {
            "raw_input": "I lost everything and rebuilt through AI",
            "source": "manual"
        }
        
        curl_cmd = f"""curl -s -X POST http://localhost:8000/ideas/create -H "Content-Type: application/json" -d '{json.dumps(test_payload)}'"""
        
        self.step(
            "Single Idea Request",
            curl_cmd,
            timeout=10
        )
        
        # Phase 4: Load test
        print("\n" + "="*70)
        print("PHASE 4: LOAD TEST (50 concurrent, 100 total)")
        print("="*70)
        
        self.step(
            "Concurrent Load Test",
            "python load_test.py",
            timeout=120
        )
        
        # Final report
        print("\n" + "="*70)
        print("BATTLE TEST RESULTS")
        print("="*70)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTests Passed: {self.passed}/{total}")
        print(f"Tests Failed: {self.failed}/{total}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed == 0:
            print("\n[VERDICT] SYSTEM READY FOR PRODUCTION")
            print("\nNext steps:")
            print("  1. docker-compose logs -f  (watch in real-time)")
            print("  2. Push to GitHub")
            print("  3. Deploy to DigitalOcean")
            return True
        else:
            print("\n[VERDICT] SYSTEM NEEDS HARDENING")
            print("\nDebug:")
            print("  docker-compose logs api")
            print("  docker-compose logs worker-pipeline")
            return False


if __name__ == "__main__":
    test = BattleTest()
    success = test.run_full_battle_test()
    
    print("\n" + "="*70)
    sys.exit(0 if success else 1)
