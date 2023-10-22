from django.http import HttpResponse, HttpResponseServerError
from PIL import Image, ImageSequence
import requests
from io import BytesIO
from django.core.cache import cache


def resize_image(request):
    try:
        # Get the image URL from the 'url' query parameter
        image_url = request.GET.get('url')

        if not image_url:
            return HttpResponse(
                "Please provide a valid 'url' query parameter.", status=400)

        # Check if the resized image is in the cache
        cache_key = f'resized_image:{image_url}'
        cached_image = cache.get(cache_key)

        if cached_image:
            return HttpResponse(cached_image, content_type='image/gif')

        # Download the original image from the URL
        response = requests.get(image_url)

        if response.status_code != 200:
            return HttpResponse(f"Failed to fetch the image from {image_url}",
                                status=500)

        # Open the image using BytesIO to support both images and GIFs
        original_image = Image.open(BytesIO(response.content))

        # Preserve the original orientation (angle)
        if hasattr(original_image, '_getexif'):
            exif = original_image._getexif()
            if exif:
                orientation = exif.get(0x0112, 1)
                if orientation == 3:
                    original_image = original_image.rotate(180, expand=True)
                elif orientation == 6:
                    original_image = original_image.rotate(270, expand=True)
                elif orientation == 8:
                    original_image = original_image.rotate(90, expand=True)

        # Resize the image while preserving animation for GIFs
        if original_image.format == 'GIF':
            frames = []
            for frame in ImageSequence.Iterator(original_image):
                # Calculate the new size while maintaining aspect ratio
                max_size = (300, 300)
                width, height = frame.size
                aspect_ratio = width / height

                if width > max_size[0] or height > max_size[1]:
                    if aspect_ratio > 1:
                        new_width = max_size[0]
                        new_height = int(max_size[0] / aspect_ratio)
                    else:
                        new_height = max_size[1]
                        new_width = int(max_size[1] * aspect_ratio)
                    resized_frame = frame.resize((new_width, new_height))
                else:
                    resized_frame = frame

                frames.append(resized_frame)

            output = BytesIO()
            frames[0].save(output,
                           format='GIF',
                           save_all=True,
                           append_images=frames[1:],
                           duration=original_image.info.get('duration', 100),
                           loop=original_image.info.get('loop', 0))
            output.seek(0)
        else:
            # For non-GIF images, resize as usual
            max_width, max_height = 300, 300

            width, height = original_image.size
            if width > max_width or height > max_height:
                # Calculate new dimensions while maintaining aspect ratio
                aspect_ratio = width / height
                if width > max_width:
                    width = max_width
                    height = int(width / aspect_ratio)
                if height > max_height:
                    height = max_height
                    width = int(height * aspect_ratio)

                # Resize the image
                resized_image = original_image.resize((width, height))
            else:
                # No need to resize if the image is already smaller
                resized_image = original_image

            # Convert the resized image to bytes
            output = BytesIO()
            resized_image.save(output, format=original_image.format)
            output.seek(0)

        # Cache the resized image
        cache.set(cache_key, output.getvalue(), 3600)  # Cache for 1 hour

        # Serve the resized image directly to the client for inline display
        response = HttpResponse(output.read(), content_type=f'image/gif')
        response['Content-Disposition'] = f'inline; filename=image.gif'
        return response

    except Exception as e:
        return HttpResponseServerError(str(e))
