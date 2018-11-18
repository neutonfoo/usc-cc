# Core Variables

# School term - Concatenate year with [1 Spring], [2 Summer], [3 Fall]
term = 20191

# Autocheckout - Dangerous, use with caution
autocheckout = False

# Link to open if a class is detected as open
triggerAvailabilityAlert = False
availabilityAlertLink = 'https://www.youtube.com/watch?v=2HtiqkDpzSs'

# Time (seconds) between checks
interval = 30

# Time (seconds) to wait before a TimeoutException is thrown
timeout = 10

# Classes list
classes = [
	{
		'class': 'CSCI270',
		'sections': ('30094',),
		'checkout': False
	}
]

# For custom emails
emailTemplateFile = 'emailTemplate.html'
sectionTemplateFile = 'sectionTemplate.html'
