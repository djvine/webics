import weave
import numpy as np
import scipy.io
from matplotlib import pyplot

def precompile_weave():
    # Dummy vars for weave compilation
    n_pix = 124
    roi = [824,864]*4
    f = scipy.io.netcdf.netcdf_file('/home/david/Downloads/2xfm_0017_2xfm3__0.nc')
    buff = f.variables['array_data'].data[0,0,:].astype(np.uint16)
    res_list = np.zeros(124)
    c_code = """
    for (int i=0;i<n_pix;i++)// pix per buffer
    {
        for (int j=0;j<4;j++)// detector elements
            {
                int r_len = int(roi[j*2+1]) - int(roi[j*2]);
                printf("j: %d, r_len: %d, buff: %d\\n",j, r_len, buff[512+i*8448+j*2048+int(roi[2*j])]);
                for (int r=0;r<r_len;r++)// roi length
                    {
                        res_list[i] += buff[512+i*8448+j*2048+int(roi[j*2])+r];
                    }
            }
    }
    """
    weave.inline(c_code, ['n_pix','roi','buff','res_list'], extra_compile_args=['-O2'])
    pyplot.plot(res_list)
    print(res_list)
    pyplot.show()
precompile_weave()
