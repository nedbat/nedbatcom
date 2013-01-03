/***	
 ***	avl.c --
 ***	
 ***	The AVL height-balanced tree abstraction.
 ***	Six functions are defined:
 ***	
 ***		newavl()
 ***			returns an empty avl tree.
 ***		addnode(tree, key, data, compare)
 ***			Adds a new node to the tree given.
 ***		node = findnode(tree, key, compare)
 ***			Finds the node in the tree.
 ***		modnode(tree, key, data, compare)
 ***			Modify an existing node.
 ***		im = startiter(tree)
 ***			Starts an iteration over the nodes, returning an
 ***			iteration map.
 ***		im = nextnode(tree, im, &node)
 ***			Returns the new map, and writes a pointer to the next
 ***			node.
 ***		size = avlsize(tree)
 ***			Returns the number of nodes in the tree.
 ***	
 ***	N.Batchelder, 5/7/85.
 ***	Adapted 1/13/85.
 ***/

# include "def.h"
# include "avl.h"

/* 
 * newavl:
 * 
 * Returns an empty avl tree.
 */

avl *
newavl()
{
	avl	*leaf();

	return leaf(NullKey, NullStuff);
}

/* 
 * addnode:
 * 
 * Given a tree, a key, a value, and a comparison function, this routine adds
 * a new node to the tree with the key and value as given. If the key already
 * exists in the tree, the new data overwrites the old. No indication of this
 * is returned to the user.
 * 
 * The value returned is useless to the caller. It is used to pass information
 * up through recursive calls.
 */

int			/* 0 means no height change, 1 means got bigger */
addnode(root, key, newval, cfn)
avl	**root;		/* Points to the tree in which to insert the node */
keystuf	key;		/* Used in the comparison function */
stuff	newval;		/* The value to insert */
int	(*cfn)();	/* The function to compare nodes */
{
	int	chosen;		/* The son which we recurred down */
	int	result;		/* The result of the comparison */
	avl	*p1, *p2;	/* To help shift things around */
	avl	*leaf();	/* The function which gives us a new leaf */

# define other	1-chosen	/* The one we didn't recur down. */
# define p	(*root)		/* To match Wirth's code */

	/* 
	 * If we have an empty tree, then we can just make the new node be the
	 * tree itself.
	 */
	
	if (p == NullTree) {
		p = leaf(key, newval);
		return 1;	/* We got higher */
	}

	/* 
	 * A leaf with NullKey for the user's key is considered equivalent
	 * to an empty tree.
	 */

	if (p->ukey == NullKey) {
		p->bal = 2;
		p->ukey = key;
		p->udata = newval;
		return 0;	/* We're the same height */
	}

	/* 
	 * There are sons, so compare data to find out which branch to take.
	 */

	result = (*cfn)(key, p->ukey);

	if (result < 0) {
		chosen = 0;
	} else if (result > 0) {
		chosen = 1;
	} else {
		/* 
		 * The new node is the same as this one, but we'll replace the
		 * old one anyway, since the user will probably have data that
		 * is not being compared.
		 */

		p->udata = newval;
		return 0;			/* Height didn't change */
	}

	/* 
	 * Now that we know which way to go, we recur.
	 */
	
	if (addnode(&(p->son[chosen]), key, newval, cfn)) {
		/*
		 * The height of the subtree changed, check the balance.
		 */

		if (p->bal == 2) {
			/*
			 * If things were balanced before, now the chosen son
			 * is heavier, so make a note of that.
			 */

			p->bal = chosen;
			return 1;

		} else if (p->bal == other) {
			/*
			 * If the other son was heavier before, now they are
			 * balanced.
			 */

			p->bal = 2;
			return 0;

		} else {
			/*
			 * The chosen son was the heavier, so now it is off by
			 * two, meaning we have violated the AVL condition, so
			 * rebalancing is necessary.
			 */

			p1 = p->son[chosen];
			if (p1->bal == chosen) {
				/*
				 * The outside subtree is too heavy. Do what
				 * Wirth calls a single rotation.
				 */

				p->son[chosen] = p1->son[other];
				p1->son[other] = p;
				p->bal = 2;
				p = p1;
			} else {
				/*
				 * The inside subtree is too heavy, so perform
				 * a double rotation.
				 */

				p2 = p1->son[other];
				p1->son[other] = p2->son[chosen];
				p2->son[chosen] = p1;
				p->son[chosen] = p2->son[other];
				p2->son[other] = p;
				if (p2->bal == chosen)
					p->bal = other;
				else
					p->bal = 2;
				if (p2->bal == other)
					p1->bal = chosen;
				else
					p1->bal = 2;
				p = p2;
			}

			/*
			 * In any case, p is now balanced perfectly,
			 * so record that, and let the upper levels know that
			 * the tree hasn't changed height
			 */

			p->bal = 2;
			return 0;
		}
	} else {
		/* 
		 * Since the height of the subtree didn't change, the height
		 * of the whole tree didn't change.
		 */

		return 0;
	}
}

/* 
 * This array and pointer form our somewhat simple-minded allocation scheme.
 */

avl	pool[10000];
int	nextavl = 0;

/* 
 * leaf:
 * 
 * Given some user data, leaf returns a new avl node ready to be inserted into
 * a tree. Leaf should only be called from inside Addnode.
 */

private
avl *
leaf(k, v)
keystuf	k;
stuff	v;
{
	avl	*t;

	t = &pool[nextavl++];
	t->son[0] = t->son[1] = NullTree;
	t->bal = 2;
	t->ukey = k;
	t->udata = v;

	return t;
}

/* 
 * findnode:
 * 
 * Given a tree, a piece of user data and a comparison function, findnode
 * returns the node in the tree which compares equal to the given one. A
 * value of zero is returned if none is found.
 */

stuff
findnode(tree, key, cfn)
avl	*tree;
keystuf	key;
int	(*cfn)();
{
	int	result;

	/* 
	 * We just keep walking down the tree, picking the right way based on
	 * the values of the nodes we reach, until we fall off an end (didn't
	 * find it), or we hit one that compares as equal.
	 */
	
	while ((tree != NullTree) && (tree->ukey != NullKey)) {
		result = (*cfn)(key, tree->ukey);

		if (result < 0) {
			tree = tree->son[0];
		} else if (result > 0) {
			tree = tree->son[1];
		} else { /* result == 0 */
			return tree->udata;
		}
	}

	return (stuff) 0;
}		

/* 
 * modnode:
 * 
 * Takes a tree, a key, a value and a comparison function. A node with the
 * given key is located, and its value is set to be the given value. The old
 * value is returned. If no node exists in the tree, zero is returned.
 */

stuff
modnode(tree, key, value, cfn)
avl	*tree;
keystuf	key;
stuff	value;
int	(*cfn)();
{
	int	result;
	stuff	old;

	/* 
	 * We just keep walking down the tree, picking the right way based on
	 * the values of the nodes we reach, until we fall off an end (didn't
	 * find it), or we hit one that compares as equal.
	 */
	
	while ((tree != NullTree) && (tree->ukey != NullKey)) {
		result = (*cfn)(key, tree->ukey);

		if (result < 0) {
			tree = tree->son[0];
		} else if (result > 0) {
			tree = tree->son[1];
		} else { /* result == 0 */
			old = tree->udata;
			tree->udata = value;
			return old;
		}
	}

	return (stuff) 0;
}		

/* 
 * startiter:
 * 
 * Takes a tree and returns an iteration map ready to be used by nextnode. The
 * map is simply an unsigned integer which leads us to the next node to be
 * returned. The bits of the map direct us through the tree:
 * 
 * 	0:	follow your lesser son.
 * 	1:	follow your greater son.
 */

imap
startiter(tree)
avl	*tree;
{
	return (imap) 0;
}

/* 
 * nextnode:
 * 
 * Recursively uses the imap presented to find the next node. A value of
 * NoMore coming back means that there are no more in this tree.
 */

imap
nextnode(tree, im, kptr, vptr)
avl	*tree;
imap	im;
keystuf	*kptr;
stuff	*vptr;
{
	fast imap	sonmap;
	
	/* 
	 * If we were given an empty tree, there are no more nodes.
	 */

	if (tree == NullTree || tree->ukey == NullStuff) {
		return NoMore;
	}

	/* 
	 * Otherwise we pick a direction based on the bit in the imap.
	 */
	
	if ((im & 1) == 0) {
		sonmap = nextnode(tree->son[0], im >> 1, kptr, vptr);
		if (sonmap == NoMore) {
			*kptr = tree->ukey;
			*vptr = tree->udata;
			return (imap) 1;
		} else {
			return (imap)(sonmap << 1);
		}
	} else {
		sonmap = nextnode(tree->son[1], im >> 1, kptr, vptr);
		if (sonmap == NoMore) {
			return NoMore;
		} else {
			return (imap)((sonmap << 1) | 1);
		}
	}
}

/* 
 * avlsize:
 * 
 * Counts the number of nodes in a tree.
 */

int
avlsize(tree)
avl	*tree;
{
	if (tree == NullTree || tree->ukey == NullKey) {
		return 0;
	} else {
		return avlsize(tree->son[0]) + avlsize(tree->son[1]) + 1;
	}
}
	
# ifdef TESTAVL

/* 
 * The code that follows is used to test the avl code. It only checks addnode,
 * actually, but so what?
 */

# include <stdio.h>

/* The main procedure */

main()
{
	int	val;
	avl	*tree = NullTree;
	int	icmp();
	
	while (scanf("%d\n", &val) != EOF) {
		addnode(&tree, val, val, icmp);
	}

	printavl(tree);
}

/* This function prints a tree on the terminal.
	Height and value are given for each node.
*/

char	ties[20];

printavl(t)
avl	*t;
{
	strcpy(ties, "                   ");
	pavl(t, 0, 0);
}

pavl(t,d,left)
avl	*t;
int	d;	/* The depth on the screen */
int	left;	/* Is this a left child? */
{
	int	i;

	if (t == NullTree) {
		ties[d] = ' ';
		return;
	}

	pavl(t->son[0], d+1, 1);

	for (i = 0; i < d; i++)
		printf("%c\t", ties[i]);
	printf("[%3d]", t->udata);
	if (t->son[0] == NullTree && t->son[1] == NullTree)
		printf("\n");
	else
		printf("---+\n");

	ties[d] = left ? '|' : ' ';

	pavl(t->son[1], d+1, 0);
}

/* The comparison function */

icmp(i1, i2)
int	i1, i2;
{
	return i2 - i1;
}

# endif TESTAVL

/* end of avl.c */
