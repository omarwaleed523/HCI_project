/*
	TUIO C# Demo - part of the reacTIVision project
	Copyright (c) 2005-2016 Martin Kaltenbrunner <martin@tuio.org>

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

using System;
using System.Drawing;
using System.Windows.Forms;
using System.ComponentModel;
using System.Collections.Generic;
using System.Collections;
using System.Threading;
using TUIO;
using System.IO;
using System.Drawing.Drawing2D;
using System.Net.Sockets;
using System.Text;



public class TuioDemo : Form, TuioListener
{
	private TuioClient client;
	private Dictionary<long, TuioObject> objectList;
	private Dictionary<long, TuioCursor> cursorList;
	private Dictionary<long, TuioBlob> blobList;

	public static int width, height;
	private int window_width = 640;
	private int window_height = 480;
	private int window_left = 0;
	private int window_top = 0;
	private int screen_width = Screen.PrimaryScreen.Bounds.Width;
	private int screen_height = Screen.PrimaryScreen.Bounds.Height;
	public int  prev_id=-1;
	private bool fullscreen;
	private bool verbose;

	public string serverIP = "DESKTOP-8161GCK"; // IP address of the Python server
	public int port = 8000;               // Port number matching the Python server
	int flag = 0;
	Font font = new Font("Arial", 10.0f);
	SolidBrush fntBrush = new SolidBrush(Color.White);
	SolidBrush bgrBrush = new SolidBrush(Color.FromArgb(0, 0, 64));
	SolidBrush curBrush = new SolidBrush(Color.FromArgb(192, 0, 192));
	SolidBrush objBrush = new SolidBrush(Color.FromArgb(64, 0, 0));
	SolidBrush blbBrush = new SolidBrush(Color.FromArgb(64, 64, 64));
	Pen curPen = new Pen(new SolidBrush(Color.Blue), 1);
	private string objectImagePath;
	private string backgroundImagePath;
	TcpClient client1;
	NetworkStream stream;
	public TuioDemo(int port)
	{

		verbose = false;
		fullscreen = false;
		width = window_width;
		height = window_height;

		this.ClientSize = new System.Drawing.Size(width, height);
		this.Name = "TuioDemo";
		this.Text = "TuioDemo";

		this.Closing += new CancelEventHandler(Form_Closing);
		this.KeyDown += new KeyEventHandler(Form_KeyDown);

		this.SetStyle(ControlStyles.AllPaintingInWmPaint |
						ControlStyles.UserPaint |
						ControlStyles.DoubleBuffer, true);

		objectList = new Dictionary<long, TuioObject>(128);
		cursorList = new Dictionary<long, TuioCursor>(128);
		blobList = new Dictionary<long, TuioBlob>(128);

		client = new TuioClient(port);
		client.addTuioListener(this);

		client.connect();

		// Create a TCP/IP socket
		 client1 = new TcpClient("LAPTOP-1SMMKPDU", 8000);
		// Get the stream to send data
		 stream = client1.GetStream();

	}
	private void Form_KeyDown(object sender, System.Windows.Forms.KeyEventArgs e)
	{

		if (e.KeyData == Keys.F1)
		{
			if (fullscreen == false)
			{

				width = screen_width;
				height = screen_height;

				window_left = this.Left;
				window_top = this.Top;

				this.FormBorderStyle = FormBorderStyle.None;
				this.Left = 0;
				this.Top = 0;
				this.Width = screen_width;
				this.Height = screen_height;

				fullscreen = true;
			}
			else
			{

				width = window_width;
				height = window_height;

				this.FormBorderStyle = FormBorderStyle.Sizable;
				this.Left = window_left;
				this.Top = window_top;
				this.Width = window_width;
				this.Height = window_height;

				fullscreen = false;
			}
		}
		else if (e.KeyData == Keys.Escape)
		{
			// Close everything
			stream.Close();
			client1.Close();
			this.Close();

		}
		else if (e.KeyData == Keys.V)
		{
			verbose = !verbose;
		}

	}

	private void Form_Closing(object sender, System.ComponentModel.CancelEventArgs e)
	{
		client.removeTuioListener(this);

		client.disconnect();
		System.Environment.Exit(0);
	}

	public void addTuioObject(TuioObject o)
	{
		lock (objectList)
		{
			objectList.Add(o.SessionID, o);
		}
		if (verbose) Console.WriteLine("add obj " + o.SymbolID + " (" + o.SessionID + ") " + o.X + " " + o.Y + " " + o.Angle);
	}

	public void updateTuioObject(TuioObject o)
	{

		if (verbose) Console.WriteLine("set obj " + o.SymbolID + " " + o.SessionID + " " + o.X + " " + o.Y + " " + o.Angle + " " + o.MotionSpeed + " " + o.RotationSpeed + " " + o.MotionAccel + " " + o.RotationAccel);
	}

	public void removeTuioObject(TuioObject o)
	{
		lock (objectList)
		{
			objectList.Remove(o.SessionID);
		}
		if (verbose) Console.WriteLine("del obj " + o.SymbolID + " (" + o.SessionID + ")");
	}

	public void addTuioCursor(TuioCursor c)
	{
		lock (cursorList)
		{
			cursorList.Add(c.SessionID, c);
		}
		if (verbose) Console.WriteLine("add cur " + c.CursorID + " (" + c.SessionID + ") " + c.X + " " + c.Y);
	}

	public void updateTuioCursor(TuioCursor c)
	{
		if (verbose) Console.WriteLine("set cur " + c.CursorID + " (" + c.SessionID + ") " + c.X + " " + c.Y + " " + c.MotionSpeed + " " + c.MotionAccel);
	}

	public void removeTuioCursor(TuioCursor c)
	{
		lock (cursorList)
		{
			cursorList.Remove(c.SessionID);
		}
		if (verbose) Console.WriteLine("del cur " + c.CursorID + " (" + c.SessionID + ")");
	}

	public void addTuioBlob(TuioBlob b)
	{
		lock (blobList)
		{
			blobList.Add(b.SessionID, b);
		}
		if (verbose) Console.WriteLine("add blb " + b.BlobID + " (" + b.SessionID + ") " + b.X + " " + b.Y + " " + b.Angle + " " + b.Width + " " + b.Height + " " + b.Area);
	}

	public void updateTuioBlob(TuioBlob b)
	{

		if (verbose) Console.WriteLine("set blb " + b.BlobID + " (" + b.SessionID + ") " + b.X + " " + b.Y + " " + b.Angle + " " + b.Width + " " + b.Height + " " + b.Area + " " + b.MotionSpeed + " " + b.RotationSpeed + " " + b.MotionAccel + " " + b.RotationAccel);
	}

	public void removeTuioBlob(TuioBlob b)
	{
		lock (blobList)
		{
			blobList.Remove(b.SessionID);
		}
		if (verbose) Console.WriteLine("del blb " + b.BlobID + " (" + b.SessionID + ")");
	}

	public void refresh(TuioTime frameTime)
	{
		Invalidate();
	}

	protected override void OnPaintBackground(PaintEventArgs pevent)
	{
		Graphics g = pevent.Graphics;
		g.FillRectangle(bgrBrush, new Rectangle(0, 0, width, height));

		List<TuioObject> visibleMarkers = new List<TuioObject>();

		lock (objectList)
		{
			foreach (TuioObject tobj in objectList.Values)
			{
				int ox = tobj.getScreenX(width);
				int oy = tobj.getScreenY(height);
				int size = height / 10;

				string objectImagePath = null;
				string backgroundImagePath = null;

				switch (tobj.SymbolID)
				{
					case 1:
						objectImagePath = Path.Combine(Environment.CurrentDirectory, "pngegg_4.png");
						backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "bg1.jpg");
						break;
					case 2:
						objectImagePath = Path.Combine(Environment.CurrentDirectory, "pngegg_5.png");
						backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "bg2.jpg");
						break;
					case 0:
					case 8:
						objectImagePath = Path.Combine(Environment.CurrentDirectory, "pngegg_3.png");
						backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "bg3.jpg");
						break;
				}

				visibleMarkers.Add(tobj);

				g.TranslateTransform(ox, oy);
				g.RotateTransform((float)(tobj.Angle / Math.PI * 180.0f));
				g.TranslateTransform(-ox, -oy);

				if (objectImagePath != null && File.Exists(objectImagePath))
				{
					using (Image objectImage = Image.FromFile(objectImagePath))
					{
						g.DrawImage(objectImage, new Rectangle(ox - size / 2, oy - size / 2, size, size));
					}
				}
				else
				{
					g.FillRectangle(objBrush, new Rectangle(ox - size / 2, oy - size / 2, size, size));
				}

				g.TranslateTransform(ox, oy);
				g.RotateTransform(-1 * (float)(tobj.Angle / Math.PI * 180.0f));
				g.TranslateTransform(-ox, -oy);
				g.DrawString(tobj.SymbolID.ToString(), font, fntBrush, new PointF(ox - 10, oy - 10));
			}
		}

		if (visibleMarkers.Count > 0)
		{
			SendMarkerData(visibleMarkers);
		}
	}

	public static void Main(String[] argv)
	{
		int port = 0;
		switch (argv.Length)
		{
			case 1:
				port = int.Parse(argv[0], null);
				if (port == 0) goto default;
				break;
			case 0:
				port = 3333;
				break;
			default:
				Console.WriteLine("usage: mono TuioDemo [port]");
				System.Environment.Exit(0);
				break;
		}

		TuioDemo app = new TuioDemo(port);
		Application.Run(app);
	}
	public void SendMarkerData(List<TuioObject> markers)
	{
		try
		{
			StringBuilder dataBuilder = new StringBuilder();
			foreach (var marker in markers)
			{
				dataBuilder.Append($"{marker.SymbolID},{marker.AngleDegrees},{marker.X},{marker.Y};");
			}

			string data = dataBuilder.ToString().TrimEnd(';');
			byte[] byteData = Encoding.UTF8.GetBytes(data);
			stream.Write(byteData, 0, byteData.Length);
			Console.WriteLine("Sent: {0}", data);
		}
		catch (Exception e)
		{
			Console.WriteLine("Exception: {0}", e);
		}
	}
}
