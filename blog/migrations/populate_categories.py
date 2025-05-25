from django.db import migrations
from django.utils.text import slugify

def create_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    
    categories_data = [
        {
            'name': 'Technology',
            'description': 'Latest trends and innovations in technology, covering hardware, software, and emerging tech.'
        },
        {
            'name': 'Web Development',
            'description': 'Topics related to web development, including HTML, CSS, JavaScript, frameworks, and best practices.'
        },
        {
            'name': 'Mobile Development',
            'description': 'Mobile app development for iOS, Android, and cross-platform frameworks.'
        },
        {
            'name': 'Artificial Intelligence',
            'description': 'Developments in AI, including neural networks, deep learning, and AI applications.'
        },
        {
            'name': 'Machine Learning',
            'description': 'Machine learning algorithms, applications, and implementation strategies.'
        },
        {
            'name': 'Data Science',
            'description': 'Data analysis, visualization, big data, and statistical modeling.'
        },
        {
            'name': 'Cloud Computing',
            'description': 'Cloud services, architecture, deployment, and management.'
        },
        {
            'name': 'DevOps',
            'description': 'Development operations, continuous integration/deployment, and automation.'
        },
        {
            'name': 'Cybersecurity',
            'description': 'Information security, threat prevention, and security best practices.'
        },
        {
            'name': 'Blockchain',
            'description': 'Blockchain technology, cryptocurrencies, and decentralized applications.'
        },
        {
            'name': 'IoT',
            'description': 'Internet of Things devices, applications, and ecosystem.'
        },
        {
            'name': 'Robotics',
            'description': 'Robotics technology, automation, and artificial intelligence in robotics.'
        },
        {
            'name': 'Software Engineering',
            'description': 'Software development principles, patterns, and best practices.'
        },
        {
            'name': 'UI/UX Design',
            'description': 'User interface design, user experience, and interaction design.'
        },
        {
            'name': 'Frontend Development',
            'description': 'Frontend technologies, frameworks, and responsive design.'
        },
        {
            'name': 'Backend Development',
            'description': 'Server-side programming, APIs, and database management.'
        },
        {
            'name': 'Database Systems',
            'description': 'Database design, management, and optimization.'
        },
        {
            'name': 'Network Security',
            'description': 'Network protection, security protocols, and threat mitigation.'
        },
        {
            'name': 'Game Development',
            'description': 'Game design, development, and gaming technologies.'
        },
        {
            'name': 'Digital Marketing',
            'description': 'Digital marketing strategies, SEO, and online presence optimization.'
        },
    ]

    for category_data in categories_data:
        Category.objects.get_or_create(
            name=category_data['name'],
            defaults={
                'slug': slugify(category_data['name']),
                'description': category_data['description']
            }
        )

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0006_alter_category_name'),  # Update this to your last migration
    ]

    operations = [
        migrations.RunPython(create_categories),
    ]