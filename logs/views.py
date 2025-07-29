from django.shortcuts import render, redirect, get_object_or_404
from .forms import LogUploadForm
from .models import LogEntry
import csv
import io
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.db.models.functions import TruncDate, ExtractHour
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from scripts.log_processor import run
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.contrib import messages
import csv, io
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import LogEntry
from .forms import LogUploadForm
from scripts.log_processor import run
from datetime import datetime
from .forms import UserUpdateForm
from .forms import CustomUserCreationForm


from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
import tempfile
import base64
from django.utils.timezone import now
import matplotlib.pyplot as plt
from .models import Notification

from django.views.decorators.http import require_POST

@login_required
#@admin_required
def upload_logs(request):
    logs = []
    anomalies = []

    if request.method == 'POST':
        form = LogUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            decoded = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            for row in reader:
                # Convert timestamp to datetime object
                try:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                except ValueError:
                    messages.error(request, f"Invalid timestamp format: {row['timestamp']}")
                    continue

                is_anomaly = 'error' in row['message'].lower() or row['level'].lower() == 'critical'
                
                log = LogEntry.objects.create(
                    user=request.user,
                    timestamp=timestamp,
                    level=row['level'],
                    message=row['message'],
                    source=row['source'],
                    is_anomaly=is_anomaly,
                )
                logs.append(log)


                # Send real-time alert if anomaly detected
                if is_anomaly:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "logs",
                        {
                            "type": "send_log",
                            "log": {
                                "level": log.level,
                                "message": log.message,
                                "timestamp": str(log.timestamp),
                            },
                        }
                    )
                    Notification.objects.create(
                        user=request.user,
                        message=f"Anomally detected in log: {log.message[:50]}..."
                    )
            # Run anomaly detection pipeline
            run()
            messages.success(request, f"Uploaded {len(logs)} logs. Anomalies: {sum(l.is_anomaly for l in logs)}")
            return redirect('logs:dashboard')
    else:
        form = LogUploadForm()

    return render(request, 'upload_logs.html', {
        'form': form,
        'logs': logs,
        'anomalies': anomalies,
    })

@login_required
def log_list(request):
    logs = LogEntry.objects.all().order_by('-timestamp')

    # Filters
    level = request.GET.get('level')
    search_query = request.GET.get('search', '').strip()
    if level:
        logs = logs.filter(level=level)
    if search_query:
        logs = logs.filter(Q(message__icontains=search_query) | Q(source__icontains=search_query))

    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'level': level,
        'search': search_query,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, '_log_list_partial.html', context)

    return render(request, 'log_list.html', context)


def export_logs_csv(request):
    logs = LogEntry.objects.all().order_by('-timestamp')
    level = request.GET.get('level')
    show_anomalies = request.GET.get('anomaly') == 'true'
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if level:
        logs = logs.filter(level=level)
    if show_anomalies:
        logs = logs.filter(is_anomaly=True)
    if start_date and end_date:
        logs = logs.filter(timestamp__range=[start_date, end_date])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Level', 'Message', 'Source', 'Anomaly'])

    for log in logs:
        writer.writerow([log.timestamp, log.level, log.message, log.source, log.is_anomaly])

    return response


def log_detail(request, pk):
    log = get_object_or_404(LogEntry, pk=pk)
    return render(request, 'log_detail.html', {'log': log})

@login_required
def dashboard_view(request):
    # Filters from query parameters
    start = request.GET.get('start')
    end = request.GET.get('end')
    show_anomalies = request.GET.get('anomaly') == 'true'

    # Role-based filtering
    if request.user.profile.role == 'admin':
        logs = LogEntry.objects.all()
    else:
        logs = LogEntry.objects.filter(user=request.user)

    # Date and anomaly filtering
    if start:
        logs = logs.filter(timestamp__date__gte=start)
    if end:
        logs = logs.filter(timestamp__date__lte=end)
    if show_anomalies:
        logs = logs.filter(is_anomaly=True)

    total_logs = logs.count()
    total_anomalies = logs.filter(is_anomaly=True).count()

    # Level-wise aggregation for summary and charts
    level_counts_qs = logs.values('level').annotate(count=Count('level'))
    level_counts = {row['level']: row['count'] for row in level_counts_qs}
    level_labels = list(level_counts.keys())
    level_values = list(level_counts.values())

    # Trend per day
    daily_logs = (logs.annotate(date=TruncDate('timestamp'))
                      .values('date').annotate(count=Count('id')).order_by('date'))
    date_labels = [entry['date'].strftime('%Y-%m-%d') for entry in daily_logs]
    date_data = [entry['count'] for entry in daily_logs]

    # Anomaly per hour (for heatmaps)
    hourly_logs = (logs.filter(is_anomaly=True)
                       .annotate(hour=ExtractHour('timestamp'))
                       .values('hour').annotate(count=Count('id'))
                       .order_by('hour'))
    hour_labels = list(range(24))
    hour_data = [0] * 24
    for row in hourly_logs:
        hour_data[row['hour']] = row['count']

    recent_logs = logs.order_by('-timestamp')[:10]

    context = {
        'total_logs': total_logs,
        'total_anomalies': total_anomalies,
        'level_counts': level_counts,
        'level_labels': level_labels,
        'level_data': level_values,
        'date_labels': date_labels,
        'date_data': date_data,
        'hour_labels': hour_labels,
        'hour_data': hour_data,
        'start': start,
        'end': end,
        'show_anomalies': show_anomalies,
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard.html', context)

def export_anomalies_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename="anomalies.csv"'
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Level', 'Message', 'Source'])
    anomalies = LogEntry.objects.filter(is_anomaly=True).order_by('-timestamp')
    for log in anomalies:
        writer.writerow([log.timestamp, log.level, log.message, log.source])
    return response


def register(request):
    if request.method=='POST':
        form=CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=CustomUserCreationForm()
    return render(request,'auth/register.html',{'form':form})

def landing_page(request):
    return render(request, 'landing.html')  # Your landing page template

@login_required
def profile_view(request):
    profile=getattr(request.user,'profile',None)

    logs_count=LogEntry.objects.filter(user=request.user).count()
    anomalies_count=LogEntry.objects.filter(user=request.user,is_anomaly=True)
    recent_logs=LogEntry.objects.filter(user=request.user).order_by('-timestamp')[:5]
    return render(request,'auth/profile.html',{
        'user':request.user,
        'profile':profile,
        'logs_count':logs_count,
        'anomalies_count':anomalies_count,
        'recent_logs':recent_logs,
    })


@login_required
def profile_edit(request):
    if request.method=='POST':
        form=UserUpdateForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,"Your profile has been updated.")
            return redirect('profile')
        
    else:
        form=UserUpdateForm(instance=request.user)

    return render(request,'auth/profile_edit.html',{
        'form':form
    })

@login_required
def export_dashboard_pdf(request):
    if request.user.profile.role == 'admin':
        log_qs = LogEntry.objects.all().order_by('-timestamp')
    else:
        log_qs = LogEntry.objects.filter(user=request.user).order_by('-timestamp')

    # Use log_qs for count/aggregation
    total_logs = log_qs.count()
    total_anomalies = log_qs.filter(is_anomaly=True).count()
    level_counts_qs = log_qs.values('level').annotate(count=Count('level'))
    level_counts = {row['level']: row['count'] for row in level_counts_qs}

    # Always assign logs
    logs = log_qs[:20]
    # Create a chart (bar chart for log levels)
    plt.figure(figsize=(6, 3))
    plt.bar(level_counts.keys(), level_counts.values(), color='skyblue')
    plt.title('Log Levels Distribution')
    plt.tight_layout()

    # Save chart to memory and convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_image = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Render HTML for PDF
    html_content = render_to_string('export_pdf.html', {
        'total_logs': total_logs,
        'total_anomalies': total_anomalies,
        'level_counts': level_counts,
        'logs': logs,
        'report_date': now().strftime("%Y-%m-%d %H:%M"),
        'chart_image': f"data:image/png;base64,{chart_image}",
    })

    # Generate PDF using WeasyPrint
    pdf_file = HTML(string=html_content).write_pdf()

    # Return response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="incident_report.pdf"'
    return response


@login_required
def notification_list(request):
    notifications=request.user.notifications.order_by('-created_at')

    notifications.update(is_read=True)

    return render(request,'notifications.html',{'notifications':notifications})

@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request,"All notifications marked as read.")
    return redirect('logs:notifications')