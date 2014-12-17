from beamon import schedule
import datetime as dt
import django
from django.utils import timezone
django.settings()

beamlines = ['2-ID-E']

# Ensure the current user is in the database
# The script queries the scheduling system and creates an entry in the database
# for the current user (PI) and experiment

now = timezone.now()
run = schedule.findRunName(now, now)
for beamline in beamlines:
    info = schedule.get_experiment_info(beamline=beamline, date=now)

    user, created = User.objects.get_or_create(
            user_id=info['user_id'],
            badge=info['badge'],
            first_name=info['first_name'],
            last_name=info['last_name'],
            email=info['email'],
            inst=info['inst'],
            inst_id=info['inst_id']
            )
    user.save()
    experiment, created = user.experiment.get_or_create(
            title=info['proposal_title'],
            proposal_id=info['proposal_id'],
            exp_type=info['experiment_type'],
            run=run,
            start_date=info['start_time'],
            end_date=info['end_time'],
            beamline=bl
            )



