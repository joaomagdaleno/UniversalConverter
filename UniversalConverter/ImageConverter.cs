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
        public bool GifLoop { get; set; } = true;
        public int JpgQuality { get; set; } = 75;
        public int PngCompression { get; set; } = 6;
        public int Width { get; set; } = 0;
        public int Height { get; set; } = 0;
        public bool KeepAspectRatio { get; set; } = true;
        public RotateMode Rotate { get; set; } = RotateMode.None;
        public bool KeepFolderStructure { get; set; } = false;
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
                image.Mutate(x =>
                {
                    if (options.Rotate != RotateMode.None)
                    {
                        x.Rotate(options.Rotate);
                    }

                    if (options.Width > 0 || options.Height > 0)
                    {
                        var resizeOptions = new ResizeOptions
                        {
                            Size = new Size(options.Width, options.Height),
                            Mode = options.KeepAspectRatio ? ResizeMode.Max : ResizeMode.Stretch
                        };
                        x.Resize(resizeOptions);
                    }
                });

                var outputStream = new MemoryStream();
                outputExtension = outputExtension.ToLower();

                switch (outputExtension)
                {
                    case ".gif":
                        var gifQuantizer = new WuQuantizer(new QuantizerOptions { MaxColors = 255, Dither = new FloydSteinbergDither() });
                        var gifEncoder = new GifEncoder { Quantizer = gifQuantizer };
                        image.Metadata.GetGifMetadata().RepeatCount = options.GifLoop ? (ushort)0 : (ushort)1;
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
                        image.SaveAsPng(outputStream, new PngEncoder { CompressionLevel = (PngCompressionLevel)options.PngCompression });
                        break;
                    default:
                        throw new NotSupportedException($"Output format '{outputExtension}' is not supported.");
                }

                outputStream.Position = 0;
                return outputStream;
            }
        }
    }
}