import torch
import torchvision

def resulting_tensor(imagesize, kernel1, pool1, out1,
                     kernel2=None, kernel3=None, kernel4=None, kernel5=None,
                     pool2=None, pool3=None, pool4=None, pool5=None,
                     out2= None, out3=None, out4 = None, out5=None):
    image = torchvision.io.read_image('4k.jpg').float()
    image = torchvision.transforms.Compose([
        torchvision.transforms.Resize(imagesize),
        torchvision.transforms.Normalize([0.5, 0.5, 0.5], [0.2, 0.2, 0.2])
    ])(image)
    print(image.shape)
    print()

    conv = torch.nn.Conv2d(3, out1, kernel1)
    image = conv(image)
    print(image.shape)
    pool = torch.nn.MaxPool2d(pool1[0], pool1[1])
    image = pool(image)
    print(image.shape)
    print()

    if kernel2 :
        conv = torch.nn.Conv2d(out1, out2, kernel2)
        image = conv(image)
        print(image.shape)
        pool = torch.nn.MaxPool2d(pool2[0], pool2[1])
        image = pool(image)
        print(image.shape)
        print()

    if kernel3:
        conv = torch.nn.Conv2d(out2, out3, kernel3)
        image = conv(image)
        print(image.shape)
        pool = torch.nn.MaxPool2d(pool3[0], pool3[1])
        image = pool(image)
        print(image.shape)
        print()

    if kernel4:
        conv = torch.nn.Conv2d(out3, out4, kernel4)
        image = conv(image)
        print(image.shape)
        pool = torch.nn.MaxPool2d(pool4[0], pool4[1])
        image = pool(image)
        print(image.shape)
        print()

    if kernel4:
        conv = torch.nn.Conv2d(out4, out5, kernel5)
        image = conv(image)
        print(image.shape)
        pool = torch.nn.MaxPool2d(pool5[0], pool5[1])
        image = pool(image)
        print(image.shape)
        print()


size = (1360, 975)
kernel1 = (10, 10)
kernel2 = (10, 10)
kernel3 = (10, 10)
kernel4 = (5, 5)
kernel5 = (5, 4)
pool1 = (5, 4)
pool2 = (5, 5)
pool3 = (3, 2)
pool4 = (2, 2)
pool5 = (2, 2)
out1 = 9
out2 = 18
out3 = 40
out4 = 80
out5 = 100

resulting_tensor(imagesize=size,
                 kernel1=kernel1, kernel2=kernel2, kernel3=kernel3, kernel4=kernel4, kernel5=kernel5,
                 pool1=pool1, pool2=pool2, pool3=pool3, pool4=pool4, pool5=pool5,
                 out1=out1, out2=out2, out3=out3, out4=out4, out5=out5)
