import random
import discord

class AdvancedMusicPlayer:
    def __init__(self):
        self.queue = []
        self.history = []
        self.current_track = None
        self.loop_mode = "off"  # off, track, queue
        self.volume = 0.8
        self.is_paused = False
        self.queue_loop = False
        
    def add_to_queue(self, track, position=None):
        if position is None:
            self.queue.append(track)
        else:
            self.queue.insert(position, track)
    
    def remove_from_queue(self, position):
        if 0 <= position < len(self.queue):
            return self.queue.pop(position)
        return None
    
    def shuffle_queue(self):
        random.shuffle(self.queue)
    
    def clear_queue(self):
        self.queue.clear()
    
    def move_track(self, from_pos, to_pos):
        if 0 <= from_pos < len(self.queue) and 0 <= to_pos < len(self.queue):
            track = self.queue.pop(from_pos)
            self.queue.insert(to_pos, track)
            return True
        return False
    
    def get_queue_info(self):
        total_duration = sum(track.duration for track in self.queue if track.duration)
        return {
            'count': len(self.queue),
            'duration': total_duration,
            'next_track': self.queue[0] if self.queue else None
        }

class AdvancedTrack:
    def __init__(self, data):
        self.title = data.get('title', 'Неизвестно')
        self.url = data.get('url')
        self.webpage_url = data.get('webpage_url')
        self.duration = data.get('duration', 0)
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader', 'Неизвестно')
        self.platform = data.get('extractor', 'unknown')
        self.requester = None
        
    def format_duration(self):
        if not self.duration:
            return "Неизвестно"
        minutes, seconds = divmod(self.duration, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    
    def create_embed(self):
        embed = discord.Embed(
            title="🎵 Сейчас играет",
            description=f"**{self.title}**",
            color=0x00ff00
        )
        embed.add_field(name="Длительность", value=self.format_duration(), inline=True)
        embed.add_field(name="Платформа", value=self.platform.upper(), inline=True)
        embed.add_field(name="Заказал", value=self.requester.mention if self.requester else "Неизвестно", inline=True)
        
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
            
        return embed