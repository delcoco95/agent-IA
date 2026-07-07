#!/usr/bin/env python3
"""
Script local pour collecter des informations système et envoyer un diagnostic à l'API BeneIT.

Ce script:
1. Collecte des informations système avec psutil (espace disque, processus, infos OS)
2. Utilise des commandes Windows natives pour les mises à jour et erreurs système
3. Affiche clairement les données collectées
4. Demande confirmation avant envoi
5. Gère les erreurs de connexion API

Usage:
    python scripts/agent_local.py
"""

import psutil
import subprocess
import json
import platform
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os


# ============================================================================
# CONFIGURATION
# ============================================================================

# URL de l'API - Modifiez pour la production
API_BASE_URL = "http://localhost:5000"
# API_BASE_URL = "https://votre-domaine.com"

# Timeout pour les requêtes API (en secondes)
API_TIMEOUT = 30


# ============================================================================
# FONCTIONS DE COLLECTE D'INFORMATIONS SYSTÈME
# ============================================================================

def get_system_info() -> Dict[str, Any]:
    """
    Collecte les informations de base sur le système.
    
    Returns:
        Dict avec les infos système (OS, version, architecture, etc.)
    """
    info = {}
    
    try:
        # Informations sur l'OS
        info["system"] = platform.system()
        info["release"] = platform.release()
        info["version"] = platform.version()
        info["architecture"] = platform.architecture()
        info["machine"] = platform.machine()
        info["processor"] = platform.processor()
        info["node_name"] = platform.node()
        
        # Informations supplémentaires avec psutil
        if hasattr(psutil, 'boot_time'):
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            info["boot_time"] = boot_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Temps de fonctionnement
        if hasattr(psutil, 'boot_time'):
            uptime_seconds = datetime.now().timestamp() - psutil.boot_time()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            info["uptime"] = f"{days} jours, {hours} heures, {minutes} minutes"
        
    except Exception as e:
        info["error"] = f"Erreur lors de la collecte des infos système: {str(e)}"
    
    return info


def get_disk_usage() -> List[Dict[str, Any]]:
    """
    Collecte l'espace disque par lecteur.
    
    Returns:
        Liste de dicts avec les infos de chaque partition
    """
    disk_info = []
    
    try:
        partitions = psutil.disk_partitions(all=False)
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent_used": usage.percent
                })
            except Exception as e:
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "error": f"Impossible de lire: {str(e)}"
                })
    except Exception as e:
        disk_info.append({"error": f"Erreur lors de la collecte disque: {str(e)}"})
    
    return disk_info


def get_top_processes(count: int = 10) -> List[Dict[str, Any]]:
    """
    Collecte les top N processus par usage CPU et RAM.
    
    Args:
        count: Nombre de processus à retourner
    
    Returns:
        Liste de dicts avec les infos des processus
    """
    processes = []
    
    try:
        # Obtenir tous les processus
        all_processes = list(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']))
        
        # Attendre un peu pour avoir des stats CPU fiables
        import time
        time.sleep(0.1)
        
        # Rafraîchir les stats CPU
        for p in all_processes:
            try:
                p.info['cpu_percent'] = p.cpu_percent(interval=0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Trier par usage CPU puis RAM
        sorted_processes = sorted(
            all_processes,
            key=lambda p: (p.info.get('cpu_percent', 0), p.info.get('memory_percent', 0)),
            reverse=True
        )[:count]
        
        for p in sorted_processes:
            try:
                info = p.info
                create_time = datetime.fromtimestamp(info['create_time']).strftime("%Y-%m-%d %H:%M:%S")
                
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "username": info.get('username') or 'N/A',
                    "cpu_percent": info.get('cpu_percent') or 0,
                    "memory_percent": info.get('memory_percent') or 0,
                    "create_time": create_time
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                processes.append({"error": f"Processus inaccessible: {str(e)}"})
        
    except Exception as e:
        processes.append({"error": f"Erreur lors de la collecte des processus: {str(e)}"})
    
    return processes


def get_memory_info() -> Dict[str, Any]:
    """
    Collecte les informations sur la mémoire.
    
    Returns:
        Dict avec les infos mémoire
    """
    memory_info = {}
    
    try:
        mem = psutil.virtual_memory()
        memory_info["total_gb"] = round(mem.total / (1024**3), 2)
        memory_info["available_gb"] = round(mem.available / (1024**3), 2)
        memory_info["used_gb"] = round(mem.used / (1024**3), 2)
        memory_info["percent_used"] = mem.percent
        
        # Mémoire swap
        swap = psutil.swap_memory()
        memory_info["swap_total_gb"] = round(swap.total / (1024**3), 2)
        memory_info["swap_used_gb"] = round(swap.used / (1024**3), 2)
        memory_info["swap_percent"] = swap.percent
        
    except Exception as e:
        memory_info["error"] = f"Erreur lors de la collecte mémoire: {str(e)}"
    
    return memory_info


def get_windows_updates() -> List[Dict[str, Any]]:
    """
    Utilise PowerShell pour obtenir les mises à jour Windows en attente.
    
    Returns:
        Liste de dicts avec les mises à jour en attente
    """
    updates = []
    
    if platform.system() != "Windows":
        updates.append({"info": "Commande disponible uniquement sur Windows"})
        return updates
    
    try:
        # Commande PowerShell pour lister les mises à jour en attente
        ps_command = """
        $Session = New-Object -ComObject Microsoft.Update.Session
        $Searcher = $Session.CreateUpdateSearcher()
        $Result = $Searcher.Search("IsInstalled=0 and Type='Software'")
        if ($Result.Updates.Count -gt 0) {
            $Result.Updates | Select-Object Title, KBArticleIDs, SizeInBytes | ConvertTo-Json
        } else {
            Write-Output '{"status": "Aucune mise à jour en attente"}'
        }
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                # Parser le JSON retourné
                import json
                parsed = json.loads(result.stdout.strip())
                if isinstance(parsed, list):
                    for update in parsed:
                        updates.append({
                            "title": update.get("Title") or "N/A",
                            "kb_articles": update.get("KBArticleIDs") or [],
                            "size_mb": round(update.get("SizeInBytes") or 0 / (1024**2), 2)
                        })
                elif isinstance(parsed, dict):
                    updates.append(parsed)
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, retourner le texte brut
                updates.append({"raw_output": result.stdout.strip()})
        else:
            updates.append({"error": f"Erreur PowerShell: {result.stderr.strip()}"})
            
    except subprocess.TimeoutExpired:
        updates.append({"error": "Timeout lors de l'exécution de PowerShell"})
    except Exception as e:
        updates.append({"error": f"Erreur lors de la collecte des mises à jour: {str(e)}"})
    
    return updates


def get_windows_event_errors() -> List[Dict[str, Any]]:
    """
    Utilise PowerShell pour obtenir les dernières erreurs critiques de l'Observateur d'événements.
    
    Returns:
        Liste de dicts avec les erreurs critiques récentes
    """
    errors = []
    
    if platform.system() != "Windows":
        errors.append({"info": "Commande disponible uniquement sur Windows"})
        return errors
    
    try:
        # Commande PowerShell pour obtenir les erreurs critiques des dernières 24h
        ps_command = """
        $24hAgo = (Get-Date).AddHours(-24)
        Get-WinEvent -FilterHashtable @{
            LogName='System','Application'
            Level=1,2  # 1=Error, 2=Warning
            StartTime=$24hAgo
        } | Select-Object TimeCreated, Id, LevelDisplayName, Source, Message | 
        Sort-Object TimeCreated -Descending | 
        Select-Object -First 20 | ConvertTo-Json -Depth 5
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                import json
                parsed = json.loads(result.stdout.strip())
                if isinstance(parsed, list):
                    for event in parsed:
                        errors.append({
                            "time": event.get("TimeCreated") or "N/A",
                            "id": event.get("Id") or "N/A",
                            "level": event.get("LevelDisplayName") or "N/A",
                            "source": event.get("Source") or "N/A",
                            "message": (event.get("Message") or "N/A")[:200] + "..." if len(event.get("Message") or "") > 200 else event.get("Message") or "N/A"
                        })
            except json.JSONDecodeError:
                errors.append({"raw_output": result.stdout.strip()})
        else:
            errors.append({"error": f"Erreur PowerShell: {result.stderr.strip()}"})
            
    except subprocess.TimeoutExpired:
        errors.append({"error": "Timeout lors de l'exécution de PowerShell"})
    except Exception as e:
        errors.append({"error": f"Erreur lors de la collecte des erreurs: {str(e)}"})
    
    return errors


def get_network_info() -> Dict[str, Any]:
    """
    Collecte les informations réseau.
    
    Returns:
        Dict avec les infos réseau
    """
    network_info = {}
    
    try:
        # Adresses IP
        addrs = psutil.net_if_addrs()
        network_info["interfaces"] = {}
        for name, addresses in addrs.items():
            network_info["interfaces"][name] = [
                {"family": addr.family.name, "address": addr.address, "netmask": addr.netmask}
                if hasattr(addr, 'netmask') else {"family": addr.family.name, "address": addr.address}
                for addr in addresses
            ]
        
        # Statistiques réseau
        net_io = psutil.net_io_counters()
        network_info["bytes_sent"] = net_io.bytes_sent
        network_info["bytes_recv"] = net_io.bytes_recv
        network_info["packets_sent"] = net_io.packets_sent
        network_info["packets_recv"] = net_io.packets_recv
        
    except Exception as e:
        network_info["error"] = f"Erreur lors de la collecte réseau: {str(e)}"
    
    return network_info


# ============================================================================
# FONCTIONS D'AFFICHAGE
# ============================================================================

def print_section(title: str):
    """Affiche un titre de section."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Affiche un sous-titre de section."""
    print(f"\n--- {title} ---")


def print_system_info(info: Dict[str, Any]):
    """Affiche les informations système."""
    print_section("INFORMATIONS SYSTÈME")
    
    for key, value in info.items():
        if key != "error":
            print(f"  {key:20}: {value}")
    
    if "error" in info:
        print(f"  ⚠ {info['error']}")


def print_disk_usage(disk_info: List[Dict[str, Any]]):
    """Affiche l'utilisation du disque."""
    print_section("ESPACE DISQUE PAR LECTEUR")
    
    if not disk_info:
        print("  Aucune information disque disponible")
        return
    
    for disk in disk_info:
        if "error" in disk:
            print(f"  ⚠ {disk['error']}")
            continue
        
        print(f"\n  Lecteur: {disk['device']} ({disk['mountpoint']})")
        print(f"    Type: {disk['fstype']}")
        print(f"    Total: {disk['total_gb']} Go")
        print(f"    Utilisé: {disk['used_gb']} Go ({disk['percent_used']}%)")
        print(f"    Libre: {disk['free_gb']} Go")


def print_memory_info(memory_info: Dict[str, Any]):
    """Affiche les informations mémoire."""
    print_section("INFORMATIONS MÉMOIRE")
    
    for key, value in memory_info.items():
        if key != "error":
            print(f"  {key:20}: {value}")
    
    if "error" in memory_info:
        print(f"  ⚠ {memory_info['error']}")


def print_top_processes(processes: List[Dict[str, Any]]):
    """Affiche les processus les plus gourmands."""
    print_section("TOP 10 PROCESSUS (CPU/RAM)")
    
    if not processes:
        print("  Aucune information processus disponible")
        return
    
    print(f"\n  {'PID':<8} {'Nom':<25} {'Utilisateur':<15} {'CPU %':<8} {'RAM %':<8} Heure de démarrage")
    print("  " + "-" * 80)
    
    for p in processes:
        if "error" in p:
            print(f"  ⚠ {p['error']}")
            continue
        
        print(f"  {p['pid']:<8} {p['name']:<25} {(p.get('username') or 'N/A'):<15} "
              f"{float(p.get('cpu_percent') or 0):<8.1f} {float(p.get('memory_percent') or 0):<8.1f} {p['create_time']}")


def print_windows_updates(updates: List[Dict[str, Any]]):
    """Affiche les mises à jour Windows en attente."""
    print_section("MISES À JOUR WINDOWS EN ATTENTE")
    
    if not updates:
        print("  Aucune information disponible")
        return
    
    for update in updates:
        if "error" in update:
            print(f"  ⚠ {update['error']}")
        elif "status" in update:
            print(f"  {update['status']}")
        elif "raw_output" in update:
            print(f"  {update['raw_output']}")
        else:
            print(f"\n  Titre: {update.get('title') or 'N/A'}")
            if update.get('kb_articles'):
                print(f"  Articles KB: {', '.join(update['kb_articles'])}")
            print(f"  Taille: {update.get('size_mb') or 0} Mo")


def print_windows_errors(errors: List[Dict[str, Any]]):
    """Affiche les erreurs critiques de l'Observateur d'événements."""
    print_section("DERNIÈRES ERREURS CRITIQUES (24h)")
    
    if not errors:
        print("  Aucune erreur disponible")
        return
    
    for error in errors:
        if "error" in error:
            print(f"  ⚠ {error['error']}")
        elif "raw_output" in error:
            print(f"  {error['raw_output']}")
        else:
            print(f"\n  [{error.get('time') or 'N/A'}] {error.get('level') or 'N/A'}")
            print(f"  Source: {error.get('source') or 'N/A'} (ID: {error.get('id') or 'N/A'})")
            print(f"  Message: {error.get('message') or 'N/A'}")


def print_network_info(network_info: Dict[str, Any]):
    """Affiche les informations réseau."""
    print_section("INFORMATIONS RÉSEAU")
    
    if "interfaces" in network_info:
        print("\n  Interfaces réseau:")
        for name, addrs in network_info["interfaces"].items():
            print(f"\n    {name}:")
            for addr in addrs:
                print(f"      {addr['family']}: {addr['address']}")
    
    if "bytes_sent" in network_info:
        print(f"\n  Trafic réseau:")
        print(f"    Octets envoyés: {network_info['bytes_sent']:,}")
        print(f"    Octets reçus: {network_info['bytes_recv']:,}")
        print(f"    Paquets envoyés: {network_info['packets_sent']:,}")
        print(f"    Paquets reçus: {network_info['packets_recv']:,}")
    
    if "error" in network_info:
        print(f"  ⚠ {network_info['error']}")


# ============================================================================
# FONCTIONS API
# ============================================================================

def send_diagnostic_to_api(data: Dict[str, Any]) -> bool:
    """
    Envoie les données de diagnostic à l'API.
    
    Args:
        data: Dict contenant toutes les données collectées
    
    Returns:
        bool: True si succès, False sinon
    """
    url = f"{API_BASE_URL}/api/diagnostic"
    
    try:
        print("\n" + "=" * 80)
        print("  ENVOI DES DONNÉES À L'API...")
        print("=" * 80)
        
        response = requests.post(
            url,
            json=data,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            print(f"\n✓ Diagnostic envoyé avec succès!")
            print(f"  Réponse: {response.json().get('message', 'OK')}")
            return True
        else:
            print(f"\n✗ Erreur API: {response.status_code}")
            print(f"  Réponse: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n✗ Timeout: L'API n'a pas répondu dans le délai imparti")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Erreur de connexion: Impossible de joindre {API_BASE_URL}")
        print(f"  Vérifiez que le serveur est en cours d'exécution")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Erreur lors de l'envoi: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ Erreur inattendue: {str(e)}")
        return False


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def collect_and_send_diagnostic():
    """
    Fonction principale: collecte toutes les données et propose l'envoi.
    """
    print("\n" + "=" * 80)
    print("  AGENT LOCAL BENEIT - COLLECTE DE DIAGNOSTIC")
    print("=" * 80)
    
    # Collecte de toutes les données
    print("\n🔍 Collecte des informations en cours...")
    
    diagnostic_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_info": get_system_info(),
        "disk_usage": get_disk_usage(),
        "memory_info": get_memory_info(),
        "top_processes": get_top_processes(10),
        "network_info": get_network_info()
    }
    
    # Ajouter les infos Windows si applicable
    if platform.system() == "Windows":
        diagnostic_data["windows_updates"] = get_windows_updates()
        diagnostic_data["windows_errors"] = get_windows_event_errors()
    
    # Afficher toutes les données collectées
    print("\n" + "=" * 80)
    print("  DONNÉES COLLECTÉES")
    print("=" * 80)
    
    print_system_info(diagnostic_data["system_info"])
    print_disk_usage(diagnostic_data["disk_usage"])
    print_memory_info(diagnostic_data["memory_info"])
    print_top_processes(diagnostic_data["top_processes"])
    print_network_info(diagnostic_data["network_info"])
    
    if platform.system() == "Windows":
        print_windows_updates(diagnostic_data["windows_updates"])
        print_windows_errors(diagnostic_data["windows_errors"])
    
    # Demander confirmation
    print("\n" + "=" * 80)
    print("  CONFIRMATION REQUISE")
    print("=" * 80)
    print("\n⚠ ATTENTION: Ces données contiennent des informations sensibles sur votre système.")
    print("  Elles seront envoyées à l'API BeneIT pour analyse.")
    print(f"\n  URL de destination: {API_BASE_URL}/api/diagnostic")
    
    while True:
        response = input("\nSouhaitez-vous envoyer ces données? (oui/non): ").strip().lower()
        
        if response in ['oui', 'o', 'yes', 'y']:
            success = send_diagnostic_to_api(diagnostic_data)
            if success:
                print("\n✓ Diagnostic envoyé avec succès!")
            else:
                print("\n✗ Échec de l'envoi du diagnostic")
            break
        elif response in ['non', 'n', 'no']:
            print("\n✓ Envoi annulé. Aucune donnée n'a été envoyée.")
            break
        else:
            print("Réponse non reconnue. Veuillez répondre par 'oui' ou 'non'.")


def main():
    """
    Point d'entrée principal.
    """
    # Vérifier que psutil est installé
    try:
        import psutil
    except ImportError:
        print("✗ Erreur: Le module 'psutil' est requis.")
        print("  Installez-le avec: pip install psutil")
        sys.exit(1)
    
    # Vérifier que requests est installé
    try:
        import requests
    except ImportError:
        print("✗ Erreur: Le module 'requests' est requis.")
        print("  Installez-le avec: pip install requests")
        sys.exit(1)
    
    # Vérifier la plateforme
    if platform.system() != "Windows":
        print("⚠ Attention: Certaines fonctionnalités (mises à jour, erreurs système) ")
        print("  ne sont disponibles que sur Windows.")
        print("  Le script fonctionnera mais avec des données limitées.\n")
    
    # Exécuter la collecte et l'envoi
    collect_and_send_diagnostic()


if __name__ == "__main__":
    main()
