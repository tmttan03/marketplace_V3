from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

# New imports added for ClusterTaggableManager, TaggedItemBase, MultiFieldPanel

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

@register_snippet
class PostCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'product categories'


class PostIndexPage(RoutablePageMixin, Page):
    """
    Index page for posts.
    We need to alter the page model's context to return the child page objects,
    the BlogPage objects, so that it works as an index page

    RoutablePageMixin is used to allow for a custom sub-URL for the tag views
    defined above.
    """
    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
    ]

    # Speficies that only BlogPage objects can live under this index page
    subpage_types = ['PostPage']

    # Defines a method to access the children of the page (e.g. BlogPage
    # objects). On the demo site we use this on the HomePage
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # http://docs.wagtail.io/en/latest/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(PostIndexPage, self).get_context(request)
        context['posts'] = PostPage.objects.descendant_of(
            self).live().order_by(
            '-date')
        return context

    # This defines a Custom view that utilizes Tags. This view will return all
    # related BlogPages for a given Tag or redirect back to the BlogIndexPage.
    # More information on RoutablePages is at
    # http://docs.wagtail.io/en/latest/reference/contrib/routablepage.html
    
    @route('^tags/$', name='tag_archive')
    @route('^tags/([\w-]+)/$', name='tag_archive')
    def tag_archive(self, request, tag=None):

        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no posts tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {
            'tag': tag,
            'posts': posts
        }
        return render(request, 'posts/post_index_page.html', context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child BlogPage objects for this BlogPageIndex.
    # If a tag is used then it will filter the posts by tag.
    def get_posts(self, tag=None):
        posts = PostPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts

    # Returns the list of Tags for all child posts of this BlogPage.
    def get_child_tags(self):
        tags = []
        for post in self.get_posts():
            # Not tags.append() because we don't want a list of lists
            tags += post.get_tags
        tags = sorted(set(tags))
        return tags


class PostPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the PostPage object and tags. There's a longer guide on using it at
    http://docs.wagtail.io/en/latest/reference/pages/model_recipes.html#tagging
    """
    content_object = ParentalKey('PostPage', related_name='tagged_items', on_delete=models.CASCADE)


class PostPage(Page):
    date = models.DateField("Post date")
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=PostPageTag, blank=True)
    categories = models.ForeignKey('posts.PostCategory', blank=True, null=True, on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=250, default="Davao")
    seller = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('body')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('price'),
            FieldPanel('location'),
            FieldPanel('seller'),
            FieldPanel('categories'),
            FieldPanel('tags'),
        ], heading="Post information"),
        InlinePanel('gallery_images', label="Gallery images"),
        
    ]

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """
        tags = self.tags.all()
        for tag in tags:
            tag.url = '/'+'/'.join(s.strip('/') for s in [
                self.get_parent().url,
                'tags',
                tag.slug
            ])
        return tags

    # Specifies parent to BlogPage as being BlogIndexPages
    parent_page_types = ['PostIndexPage']

    # Specifies what content types can exist as children of BlogPage.
    # Empty list means that no child content types are allowed.
    subpage_types = []

    
class PostPageGalleryImage(Orderable):
    page = ParentalKey(PostPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


class TagsIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = PostPage.objects.filter(tags__name=tag)

        # Update template context
        #context = super().get_context(request)
        #context['blogpages'] = blogpages
        return context