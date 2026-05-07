import json
import os
from datetime import datetime
from pathlib import Path
from config import DATA_DIR

class PersistenceManager:
    """Handles memory backup and recovery across restarts."""
    
    def __init__(self):
        self.backup_dir = os.path.join(DATA_DIR, "backups")
        self.latest_backup = os.path.join(self.backup_dir, "latest_memories.json")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_memories(self, memories_data):
        """Create a timestamped backup of memories."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"backup_{timestamp}.json")
        
        with open(backup_file, 'w') as f:
            json.dump(memories_data, f, indent=2)
        
        # Also write to latest
        with open(self.latest_backup, 'w') as f:
            json.dump(memories_data, f, indent=2)
        
        return backup_file
    
    def restore_latest(self):
        """Restore from latest backup."""
        if os.path.exists(self.latest_backup):
            with open(self.latest_backup, 'r') as f:
                return json.load(f)
        return None
    
    def get_backups(self):
        """List all backups."""
        backups = []
        for f in os.listdir(self.backup_dir):
            if f.startswith('backup_') and f.endswith('.json'):
                backups.append(f)
        return sorted(backups, reverse=True)
    
    def restore_from_backup(self, backup_name):
        """Restore from specific backup."""
        backup_file = os.path.join(self.backup_dir, backup_name)
        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                return json.load(f)
        return None
