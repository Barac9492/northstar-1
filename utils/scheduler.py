import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone=pytz.timezone(os.environ.get('TIMEZONE', 'UTC'))
        )
        self.scheduler.start()
        self.jobs = {}
        
    def schedule_post(self, content: str, platform: str, 
                     scheduled_time: str, repeat: Optional[str] = None) -> str:
        try:
            job_id = f"{platform}_{datetime.utcnow().timestamp()}"
            
            scheduled_dt = datetime.fromisoformat(scheduled_time)
            
            if repeat == 'daily':
                trigger = IntervalTrigger(days=1, start_date=scheduled_dt)
            elif repeat == 'weekly':
                trigger = IntervalTrigger(weeks=1, start_date=scheduled_dt)
            elif repeat == 'hourly':
                trigger = IntervalTrigger(hours=1, start_date=scheduled_dt)
            else:
                trigger = DateTrigger(run_date=scheduled_dt)
            
            job = self.scheduler.add_job(
                func=self._execute_post,
                trigger=trigger,
                args=[content, platform],
                id=job_id,
                name=f"Post to {platform}",
                misfire_grace_time=300
            )
            
            self.jobs[job_id] = {
                'content': content,
                'platform': platform,
                'scheduled_time': scheduled_time,
                'repeat': repeat,
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scheduled post {job_id} for {scheduled_time}")
            return job_id
            
        except Exception as e:
            logger.error(f"Scheduling error: {e}")
            raise
    
    def _execute_post(self, content: str, platform: str):
        try:
            logger.info(f"Executing scheduled post for {platform}")
            
            if platform.lower() == 'twitter':
                from integrations.twitter_api import TwitterAPI
                api = TwitterAPI()
                result = api.post_tweet(content)
            elif platform.lower() == 'instagram':
                from integrations.instagram_api import InstagramAPI
                api = InstagramAPI()
                result = api.create_post(content)
            else:
                logger.warning(f"Unsupported platform: {platform}")
                return
            
            if result.get('success'):
                logger.info(f"Successfully posted to {platform}")
                self._update_job_status(platform, 'completed')
            else:
                logger.error(f"Failed to post to {platform}: {result.get('error')}")
                self._update_job_status(platform, 'failed')
                
        except Exception as e:
            logger.error(f"Post execution error: {e}")
            self._update_job_status(platform, 'failed')
    
    def _update_job_status(self, platform: str, status: str):
        for job_id, job_data in self.jobs.items():
            if job_data['platform'] == platform and job_data['status'] == 'scheduled':
                job_data['status'] = status
                job_data['executed_at'] = datetime.utcnow().isoformat()
                break
    
    def cancel_job(self, job_id: str) -> bool:
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                self.jobs[job_id]['status'] = 'cancelled'
                self.jobs[job_id]['cancelled_at'] = datetime.utcnow().isoformat()
            logger.info(f"Cancelled job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {e}")
            return False
    
    def reschedule_job(self, job_id: str, new_time: str) -> bool:
        try:
            if job_id not in self.jobs:
                return False
            
            job_data = self.jobs[job_id]
            new_dt = datetime.fromisoformat(new_time)
            
            self.scheduler.reschedule_job(
                job_id,
                trigger=DateTrigger(run_date=new_dt)
            )
            
            job_data['scheduled_time'] = new_time
            job_data['rescheduled_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Rescheduled job {job_id} to {new_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error rescheduling job {job_id}: {e}")
            return False
    
    def get_scheduled_jobs(self, platform: Optional[str] = None) -> List[Dict]:
        jobs = []
        
        for job in self.scheduler.get_jobs():
            job_data = self.jobs.get(job.id, {})
            
            if platform and job_data.get('platform') != platform:
                continue
            
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'platform': job_data.get('platform'),
                'content': job_data.get('content', '')[:100],
                'repeat': job_data.get('repeat'),
                'status': job_data.get('status', 'scheduled')
            })
        
        return jobs
    
    def get_job_stats(self) -> Dict:
        total_jobs = len(self.jobs)
        scheduled = sum(1 for j in self.jobs.values() if j['status'] == 'scheduled')
        completed = sum(1 for j in self.jobs.values() if j['status'] == 'completed')
        failed = sum(1 for j in self.jobs.values() if j['status'] == 'failed')
        cancelled = sum(1 for j in self.jobs.values() if j['status'] == 'cancelled')
        
        return {
            'total': total_jobs,
            'scheduled': scheduled,
            'completed': completed,
            'failed': failed,
            'cancelled': cancelled,
            'success_rate': (completed / max(completed + failed, 1)) * 100
        }
    
    def add_optimal_time_scheduling(self, content: str, platform: str) -> str:
        optimal_times = {
            'twitter': ['09:00', '14:00', '20:00'],
            'instagram': ['11:00', '19:00'],
            'linkedin': ['08:00', '12:00', '17:00']
        }
        
        platform_times = optimal_times.get(platform.lower(), ['12:00'])
        
        now = datetime.utcnow()
        next_optimal = None
        
        for time_str in platform_times:
            hour, minute = map(int, time_str.split(':'))
            potential_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if potential_time > now:
                next_optimal = potential_time
                break
        
        if not next_optimal:
            hour, minute = map(int, platform_times[0].split(':'))
            next_optimal = (now + timedelta(days=1)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
        
        return self.schedule_post(content, platform, next_optimal.isoformat())
    
    def bulk_schedule(self, posts: List[Dict]) -> List[str]:
        job_ids = []
        
        for post in posts:
            try:
                job_id = self.schedule_post(
                    content=post['content'],
                    platform=post['platform'],
                    scheduled_time=post['scheduled_time'],
                    repeat=post.get('repeat')
                )
                job_ids.append(job_id)
            except Exception as e:
                logger.error(f"Error scheduling bulk post: {e}")
                job_ids.append(None)
        
        return job_ids
    
    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("Scheduler shut down")


class ContentQueue:
    def __init__(self):
        self.queue = []
        self.processed = []
        
    def add_to_queue(self, content: Dict):
        content['queued_at'] = datetime.utcnow().isoformat()
        content['queue_id'] = f"queue_{datetime.utcnow().timestamp()}"
        self.queue.append(content)
        return content['queue_id']
    
    def get_next(self, platform: Optional[str] = None) -> Optional[Dict]:
        for item in self.queue:
            if not platform or item.get('platform') == platform:
                self.queue.remove(item)
                item['processed_at'] = datetime.utcnow().isoformat()
                self.processed.append(item)
                return item
        return None
    
    def get_queue_size(self, platform: Optional[str] = None) -> int:
        if not platform:
            return len(self.queue)
        return sum(1 for item in self.queue if item.get('platform') == platform)
    
    def clear_queue(self, platform: Optional[str] = None):
        if not platform:
            self.queue.clear()
        else:
            self.queue = [item for item in self.queue if item.get('platform') != platform]