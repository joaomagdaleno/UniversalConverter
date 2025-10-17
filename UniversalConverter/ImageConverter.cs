using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Processing;
using SixLabors.ImageSharp.Formats.Gif;
using SixLabors.ImageSharp.Formats.Webp;
using SixLabors.ImageSharp.Formats.Png;
using SixLabors.ImageSharp.Formats.Jpeg;
using SixLabors.ImageSharp.Processing.Processors.Quantization;
using System.IO;

namespace UniversalConverter
{
    public class ConversionOptions
    {
        public int WebpQuality { get; set; } = 75;
        public ushort GifRepeatCount { get; set; } = 0;
        public int JpgQuality { get; set; } = 75;
        public PngCompressionLevel PngCompression { get; set; } = PngCompressionLevel.Default;
        public int Width { get; set; } = 0;
        public int Height { get; set; } = 0;
        public bool KeepAspectRatio { get; set; } = true;
    }

    public class ImageConverter
    {
        public void ConvertImage(string inputPath, string outputPath, ConversionOptions options)
        {
            using (var stream = ConvertImageToStream(inputPath, Path.GetExtension(outputPath), options))
            {
                using (var fileStream = new FileStream(outputPath, FileMode.Create))
                {
                    stream.CopyTo(fileStream);
                }
            }
        }

        public MemoryStream ConvertImageToStream(string inputPath, string outputExtension, ConversionOptions options)
        {
            using (Image image = Image.Load(inputPath))
            {
                if (options.Width > 0 || options.Height > 0)
                {
                    var resizeOptions = new ResizeOptions
                    {
                        Size = new Size(options.Width, options.Height),
                        Mode = options.KeepAspectRatio ? ResizeMode.Max : ResizeMode.Stretch
                    };
                    image.Mutate(x => x.Resize(resizeOptions));
                }

                var outputStream = new MemoryStream();
                outputExtension = outputExtension.ToLower();

                switch (outputExtension)
                {
                    case ".gif":
                        var gifQuantizer = new WuQuantizer(new QuantizerOptions { MaxColors = 255, Dither = new FloydSteinbergDither() });
                        var gifEncoder = new GifEncoder { Quantizer = gifQuantizer };
                        image.Metadata.GetGifMetadata().RepeatCount = options.GifRepeatCount;
                        image.SaveAsGif(outputStream, gifEncoder);
                        break;
                    case ".webp":
                        image.SaveAsWebp(outputStream, new WebpEncoder { Quality = options.WebpQuality });
                        break;
                    case ".jpg":
                    case ".jpeg":
                        image.SaveAsJpeg(outputStream, new JpegEncoder { Quality = options.JpgQuality });
                        break;
                    case ".png":
                        image.SaveAsPng(outputStream, new PngEncoder { CompressionLevel = options.PngCompression });
                        break;
                    default:
                        throw new NotSupportedException($"Formato de saída '{outputExtension}' não é suportado.");
                }

                outputStream.Position = 0;
                return outputStream;
            }
        }
    }
}