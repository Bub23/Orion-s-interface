#!/usr/bin/env python
"""
Sound Savage AI - Production Load Test Harness
Simulates real traffic, validates pipeline under pressure
"""

import asyncio
import time
import json
from datetime import datetime
import statistics
from typing import List, Dict

import httpx


class LoadTestConfig:
    """Test configuration"""
    API_URL = "http://localhost:8000"
    CONCURRENT_REQUESTS = 50
    TOTAL_REQUESTS = 100
    TIMEOUT = 30
    
    TEST_IDEAS = [
        "I lost everything and rebuilt my life through AI music and hustle",
        "This AI tool replaced my entire workflow in 48 hours",
        "Building a $100K side hustle with AI automation",
        "The truth about AI that nobody talks about",
        "I tested 50 AI tools and here's what actually works",
        "This algorithm changed how I create content forever",
        "How I went from broke to profitable using AI",
        "The dirty secret about content creation nobody mentions",
        "I automated 90% of my business with these AI tools",
        "Here's why traditional marketing is dead",
    ]


class LoadTestMetrics:
    """Collect and analyze test metrics"""
    
    def __init__(self):
        self.requests: List[Dict] = []
        self.start_time = None
        self.end_time = None
        self.errors: List[str] = []
        self.successes = 0
        self.failures = 0
    
    def add_request(self, task_id: str, duration: float, status: str, error: str = None):
        """Record request metrics"""
        self.requests.append({
            "task_id": task_id,
            "duration_ms": duration * 1000,
            "status": status,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        if status == "success":
            self.successes += 1
        else:
            self.failures += 1
            if error:
                self.errors.append(error)
    
    def report(self):
        """Generate performance report"""
        if not self.requests:
            print("\n[FAIL] No requests recorded")
            return
        
        durations = [r["duration_ms"] for r in self.requests]
        
        total_time = self.end_time - self.start_time
        throughput = len(self.requests) / total_time
        
        print("\n" + "="*70)
        print("LOAD TEST RESULTS")
        print("="*70)
        
        print(f"\n[REQUESTS]")
        print(f"  Total: {len(self.requests)}")
        print(f"  Success: {self.successes}")
        print(f"  Failures: {self.failures}")
        print(f"  Success Rate: {(self.successes / len(self.requests) * 100):.1f}%")
        
        print(f"\n[TIMING]")
        print(f"  Total Duration: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} req/s")
        print(f"  Min Latency: {min(durations):.2f}ms")
        print(f"  Max Latency: {max(durations):.2f}ms")
        print(f"  Avg Latency: {statistics.mean(durations):.2f}ms")
        print(f"  P95 Latency: {sorted(durations)[int(len(durations) * 0.95)]:.2f}ms")
        print(f"  P99 Latency: {sorted(durations)[int(len(durations) * 0.99)]:.2f}ms")
        
        if self.errors:
            print(f"\n[ERRORS ({len(set(self.errors))} unique)]")
            for error in list(set(self.errors))[:5]:
                print(f"  - {error}")
        
        print(f"\n[PIPELINE VALIDATION]")
        print(f"  API reachable: {'YES' if self.successes > 0 else 'NO'}")
        print(f"  Queue functional: {'YES' if self.successes > 0 else 'UNKNOWN'}")
        print(f"  Error handling: {'CLEAN' if len(self.errors) == 0 else 'NEEDS WORK'}")
        
        print("\n" + "="*70)
        
        # Return pass/fail
        if self.successes >= len(self.requests) * 0.95:
            print("[PASS] System ready for production")
            return True
        else:
            print("[FAIL] System needs hardening before deploy")
            return False


class LoadTestRunner:
    """Execute load test"""
    
    def __init__(self):
        self.metrics = LoadTestMetrics()
        self.client = None
    
    async def test_single_request(self, idea: str, request_num: int) -> Dict:
        """Test single request"""
        start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=LoadTestConfig.TIMEOUT) as client:
                response = await client.post(
                    f"{LoadTestConfig.API_URL}/ideas/create",
                    json={"raw_input": idea, "source": "manual"},
                    headers={"Content-Type": "application/json"}
                )
            
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id", "unknown")
                self.metrics.add_request(task_id, duration, "success")
                return {"status": "success", "task_id": task_id}
            else:
                self.metrics.add_request("error", duration, "failure", f"HTTP {response.status_code}")
                return {"status": "failure", "error": f"HTTP {response.status_code}"}
        
        except asyncio.TimeoutError:
            duration = time.time() - start
            self.metrics.add_request("timeout", duration, "failure", "Request timeout")
            return {"status": "failure", "error": "timeout"}
        
        except Exception as e:
            duration = time.time() - start
            self.metrics.add_request("error", duration, "failure", str(e))
            return {"status": "failure", "error": str(e)}
    
    async def run_concurrent_batch(self, batch_num: int):
        """Run batch of concurrent requests"""
        print(f"\n[BATCH {batch_num}] Firing {LoadTestConfig.CONCURRENT_REQUESTS} concurrent requests...")
        
        tasks = []
        for i in range(LoadTestConfig.CONCURRENT_REQUESTS):
            idea = LoadTestConfig.TEST_IDEAS[i % len(LoadTestConfig.TEST_IDEAS)]
            task = self.test_single_request(idea, i)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        successes = sum(1 for r in results if r["status"] == "success")
        print(f"  Results: {successes}/{LoadTestConfig.CONCURRENT_REQUESTS} succeeded")
        
        return results
    
    async def run_full_test(self):
        """Run complete load test"""
        print("\n" + "="*70)
        print("SOUND SAVAGE AI - PRODUCTION LOAD TEST")
        print("="*70)
        
        # Check API is reachable
        print("\n[STARTUP] Checking API availability...")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{LoadTestConfig.API_URL}/health")
                if response.status_code == 200:
                    print("[OK] API is reachable")
                else:
                    print("[FAIL] API returned non-200 status")
                    return False
        except Exception as e:
            print(f"[FAIL] API unreachable: {e}")
            print(f"\nMake sure you've run: docker-compose up")
            return False
        
        # Run load test
        self.metrics.start_time = time.time()
        
        num_batches = LoadTestConfig.TOTAL_REQUESTS // LoadTestConfig.CONCURRENT_REQUESTS
        
        for batch_num in range(num_batches):
            await self.run_concurrent_batch(batch_num + 1)
            if batch_num < num_batches - 1:
                await asyncio.sleep(1)  # Brief pause between batches
        
        self.metrics.end_time = time.time()
        
        # Generate report
        return self.metrics.report()


async def main():
    """Main test entry point"""
    runner = LoadTestRunner()
    success = await runner.run_full_test()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
