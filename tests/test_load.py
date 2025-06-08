import asyncio
import httpx
import time
import statistics

async def test_endpoint(client, i):
    """Test une requête unique et retourne le temps de réponse"""
    start = time.time()
    try:
        response = await client.post(
            "http://localhost:8000/api/query",
            json={"question": f"Quelle est la hauteur maximale en zone {i % 3 + 1}?", "commune": "Test"}
        )
        if response.status_code == 200:
            return time.time() - start, True
        else:
            return time.time() - start, False
    except Exception as e:
        print(f"Erreur requête {i}: {e}")
        return time.time() - start, False

async def load_test(num_requests=50):
    """Lance un test de charge avec le nombre de requêtes spécifié"""
    print(f"🚀 Démarrage du test de charge avec {num_requests} requêtes...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Warmup
        print("⏳ Warmup...")
        await test_endpoint(client, 0)
        
        # Test concurrent
        print("🔥 Test en cours...")
        tasks = [test_endpoint(client, i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        # Analyse des résultats
        times = [r[0] for r in results]
        successes = [r[1] for r in results]
        success_rate = sum(successes) / len(successes) * 100
        
        print("\n📊 Résultats du test de charge:")
        print(f"✅ Requêtes réussies: {sum(successes)}/{num_requests} ({success_rate:.1f}%)")
        print(f"⏱️  Temps moyen: {statistics.mean(times):.3f}s")
        print(f"⏱️  Temps médian: {statistics.median(times):.3f}s")
        print(f"⏱️  Temps min: {min(times):.3f}s")
        print(f"⏱️  Temps max: {max(times):.3f}s")
        print(f"⏱️  Écart-type: {statistics.stdev(times) if len(times) > 1 else 0:.3f}s")
        print(f"⏱️  Temps total: {sum(times):.3f}s")
        
        # Calcul du débit
        total_time = max(times)  # Temps total du test
        throughput = num_requests / total_time
        print(f"📈 Débit: {throughput:.1f} req/s")

async def stress_test():
    """Test de montée en charge progressive"""
    print("🎯 Test de montée en charge progressive\n")
    
    for num_requests in [10, 25, 50, 100]:
        print(f"\n{'='*50}")
        print(f"Test avec {num_requests} requêtes concurrentes")
        print(f"{'='*50}")
        await load_test(num_requests)
        await asyncio.sleep(2)  # Pause entre les tests

async def test_cache():
    """Test spécifique du cache"""
    print("\n🔄 Test du cache\n")
    
    async with httpx.AsyncClient() as client:
        question = "Quelle est la hauteur maximale autorisée ?"
        
        # Première requête (devrait mettre en cache)
        print("1️⃣ Première requête...")
        start = time.time()
        response1 = await client.post(
            "http://localhost:8000/api/query",
            json={"question": question, "commune": "Montpellier"}
        )
        time1 = time.time() - start
        data1 = response1.json()
        print(f"   Temps: {time1:.3f}s - Cached: {data1.get('cached', False)}")
        
        # Deuxième requête (devrait être en cache)
        print("2️⃣ Deuxième requête (même question)...")
        start = time.time()
        response2 = await client.post(
            "http://localhost:8000/api/query",
            json={"question": question, "commune": "Montpellier"}
        )
        time2 = time.time() - start
        data2 = response2.json()
        print(f"   Temps: {time2:.3f}s - Cached: {data2.get('cached', False)}")
        
        # Comparaison
        if data2.get('cached'):
            speedup = time1 / time2
            print(f"\n✨ Le cache a accéléré la réponse de {speedup:.1f}x !")
        else:
            print("\n⚠️  Le cache ne semble pas fonctionner")

def main():
    """Menu principal"""
    print("""
╔═══════════════════════════════════════════╗
║   🧪 Tests de Performance - Urbanisme API  ║
╚═══════════════════════════════════════════╝

Choisissez un test:
1. Test de charge simple (50 requêtes)
2. Test de montée en charge
3. Test du cache
4. Tous les tests
""")
    
    choice = input("Votre choix (1-4): ")
    
    if choice == "1":
        asyncio.run(load_test())
    elif choice == "2":
        asyncio.run(stress_test())
    elif choice == "3":
        asyncio.run(test_cache())
    elif choice == "4":
        asyncio.run(load_test())
        asyncio.run(test_cache())
        asyncio.run(stress_test())
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    main()